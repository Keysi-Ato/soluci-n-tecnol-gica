#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from utils.InvoiceLine import Factura
from utils.Boleta import Boleta
from utils.Resumen import Resumen
from utils.NotaCredito import NotaCredito
from utils.NotaDebito import NotaDebito
import xml.etree.ElementTree as ET
from signxml import XMLSigner, XMLVerifier,methods
import requests
import zipfile
import base64
import os
from suds.client import Client
from suds.wsse import *
import requests
import logging
import time

class resumen_diario(models.Model):
    _inherit = "account.invoice"
    
    # Como coloco el modelo account.summary dentro de la variable para poder jalar sus atributos y metodos?
    # summaryObj = "account.summary" # Modelo para el resumen
    

    @api.multi
    def generarResumenDiario(self):
        ResumenDiarioObject=Resumen()
        ResumenDiario = ResumenDiarioObject.Root()

        ResumenDiario.appendChild(ResumenDiarioObject.firma(id="placeholder"))

        issue_date = time.strftime('%Y-%m-%d')

        
        ResumenDiario = ResumenDiarioObject.SummaryRoot(
            rootXML=ResumenDiario,
            ubl_version_id='2.0',
            customization_id='1.1',
            summary_id='RC-20180608-1',
            reference_date='2018-06-08',
            issue_date=issue_date,
            note='Nota de boletas'
        )
        
        ResumenDiario.appendChild(ResumenDiarioObject.Signature(
			Id="IDSignMT",
			ruc=str(self.company_id.partner_id.vat),
			razon_social=str(self.company_id.partner_id.registration_name),
			uri="#SignatureMT"))
        
        Empresa=ResumenDiarioObject.cacAccountingSupplierParty(
			num_doc_ident=str(self.company_id.partner_id.vat),
			tipo_doc_ident=str(self.company_id.partner_id.catalog_06_id.code),
			nombre_comercial=self.company_id.partner_id.registration_name,
			codigo_ubigeo=str(self.company_id.partner_id.zip),
			nombre_direccion_full=str(self.company_id.partner_id.street),
			nombre_direccion_division=self.company_id.partner_id.street2,
			nombre_departamento=str(self.company_id.partner_id.state_id.name),
			nombre_provincia=str(self.company_id.partner_id.province_id.name),
			nombre_distrito=str(self.company_id.partner_id.district_id.name),
			nombre_proveedor=str(self.company_id.partner_id.registration_name),
			codigo_pais="PE")

        ResumenDiario.appendChild(Empresa)

        # Seleccionamos los diarios de Boleta de venta
        journals_code = self.env['account.journal'].search([
            ['invoice_type_code_id', '=', '03']
            ])

        # Variable para LineId
        line_id = 1

        # Recorremos el arreglo
        for journal in journals_code:
            # Obtenemos las boletas del dia
            boleta_ids = self.env['account.invoice'].search([
                ['invoice_type_code', '=', '03'],
                ['state','in',['open', 'paid']],
                ['date_invoice', '=', '2018-06-08'],
                ['journal_id.code', '=', journal.code]
                ],order="number asc")
            
            # Asignamos los montos totales a 0
            gravado = 0
            inafecto = 0
            exonerada = 0
            amount_tax = 0

            # Si tenemos boletas dentro del arreglo
            if boleta_ids:
                # Cantidad de boletas
                l = len(boleta_ids)
                # Inicio y fin del rango de boletas
                start = int(boleta_ids[0].number[5:13])
                end = int(boleta_ids[l-1].number[5:13])

                # Recorremos el array de boletas de venta
                for boleta in boleta_ids:
                    # Acumulamos los montos totales del grupo de boletas
                    gravado = gravado + boleta.total_venta_gravado
                    inafecto = inafecto + boleta.total_venta_inafecto
                    exonerada = exonerada + boleta.total_venta_exonerada
                    amount_tax = amount_tax + boleta.amount_tax
                    # print boleta.number
                
                SummaryLine = ResumenDiarioObject.SummaryDocumentsLine(
                    line_id=line_id,
                    journal=journal.code,
                    start=start,
                    end=end,
                    gravado=gravado,
                    inafecto=inafecto,
                    exonerada=exonerada,
                    amount_tax=amount_tax)

                line_id = line_id +1

            ResumenDiario.appendChild(SummaryLine)        

        I = ResumenDiario.toprettyxml("        ")
        self.write({"documentoXML": I})

    @api.multi
    def firmarResumen(self):
        data_unsigned=ET.fromstring(self.documentoXML.encode('utf-8').strip())
        namespaces = {
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "ccts": "urn:un:unece:uncefact:documentation:2",
            "ds": "http://www.w3.org/2000/09/xmldsig#",
            "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2",
            "sac": "urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1",
            "udt": "urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2",
            "xsi": "http://www.w3.org/  2001/XMLSchema-instance",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        }

        namespaces.update({"":"urn:sunat:names:specification:ubl:peru:schema:xsd:SummaryDocuments-1"})

        for prefix, uri in namespaces.iteritems():
            ET.register_namespace(prefix, uri)
        uri="/var/lib/odoo/"
        name_file=self.company_id.partner_id.vat+"-RC-20180608-1"
        file=open(uri+name_file+".xml","w")
        signed_root = XMLSigner(
                                    method=methods.enveloped,
                                    digest_algorithm='sha1',
                                    c14n_algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
                                ).sign(data_unsigned,
                                       key=str(self.company_id.private),
                                       cert=str(self.company_id.public),
                                       )
        signed_root[0][0][0][0].set("Id","SignatureMT")
        # self.digestvalue=signed_root[0][1][0][0][0][2][2].text
        file.write(ET.tostring(signed_root))
        file.close()
        
        xfile=open(uri+name_file+".xml","r")
        xml_file = xfile.read()
        self.documentoXMLcliente=base64.b64encode(str(xml_file))
        xfile.close()
		
        zf=zipfile.ZipFile(uri+name_file+".zip",mode="w")
        try:
            zf.write(uri+name_file+".xml",arcname=name_file+".xml")
        except Exception, e:
            zf.close()
        zf.close()

        f = open(uri+name_file+".zip", 'rb')
        data_file = f.read()
        self.documentoZip=base64.b64encode(str(data_file))
        self.documentoXML=ET.tostring(signed_root)
        f.close()

        # ResumenObject = Resumen()
        # EnvioXML = ResumenObject.sendBill(username=self.company_id.partner_id.vat + self.company_id.sunat_username,
        #                        password=self.company_id.sunat_password,
        #                        namefile=name_file+".zip",
        #                        contentfile=self.documentoZip)
        # self.documentoEnvio=EnvioXML.toprettyxml("        ")
        ResumenObject = Resumen()
        EnvioXML = ResumenObject.getStatus(username=self.company_id.partner_id.vat + self.company_id.sunat_username,
                               password=self.company_id.sunat_password,
                               namefile=name_file+".zip",
                               contentfile=self.documentoZip)
        self.documentoEnvio=EnvioXML.toprettyxml("        ")

    @api.multi
    def enviarResumen(self):
        # Beta
        # url="https://e-beta.sunat.gob.pe:443/ol-ti-itcpfegem-beta/billService"
        # Homologacion
        # url="https://www.sunat.gob.pe:443/ol-ti-itcpgem-sqa/billService"
        
        # Produccion
        # URL 1
        url="https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService"
        # URL 2
        # url="https://www.sunat.gob.pe/ol-ti-itcpfegem/billService"
        # https://www.sunat.gob.pe/ol-ti-itcpgem-sqa/billService

        r=requests.post(url=url,
                        data=self.documentoEnvio,
                        headers={"Content-Type":"text/xml"})
        os.system("echo 'RESPUESTA:"+r.text+"'")
        try:
            self.documentoRespuestaZip=ET.fromstring(r.text)[0][0][0][0].text
        except Exception, e:
            self.documentoRespuestaZip=""
        self.documentoRespuesta=r.text

class invoice_boleta(models.Model):
    _inherit = "account.invoice"
    @api.multi
    def generarBoletaVenta(self):
        BoletaVentaObject=Boleta()
        Invoice = BoletaVentaObject.Root()
        Total = BoletaVentaObject.AdditionalMonetaryTotal(
            gravado=str(round(self.total_venta_gravado, 2)),
            exonerado=str(round(self.total_venta_exonerada, 2)),
            inafecto=str(round(self.total_venta_inafecto, 2)),
            gratuito=str(round(self.total_venta_gratuito, 2)),
            total_descuento=str(round(self.total_descuentos, 2)),
            currencyID=str(self.company_id.currency_id.name)
		)
        Total.appendChild(BoletaVentaObject.firma(id="placeholder"))
        Invoice.appendChild(Total)

        Invoice = BoletaVentaObject.SummaryRoot(
            rootXML=Invoice,
            ubl_version_id="2.0",
            customization_id="1.0",
            summary_id=str(self.number),
            reference_data="2018-01-23",
            issue_date=str(self.date_invoice),
            note="Note 1")
        
        signature = BoletaVentaObject.Signature(signature_id="IdSignCA",
                                                signatory_party_id=str(self.company_id.partner_id.vat),
                                                party_name=str(self.company_id.partner_id.registration_name),
                                                digital_signature_uri="SignatureUri")
        supplier_party = BoletaVentaObject.AccountingSupplierParty(customer_assigned_id=str(self.company_id.partner_id.vat),
                                                        additional_id="6",
                                                        registration_name=str(self.company_id.partner_id.registration_name))

        Invoice.appendChild(signature)
        Invoice.appendChild(supplier_party)

        array1 = []
        for tax in self.tax_line_ids:
            dict1 = {"tax_amount": str(round(tax.amount,2)), "tax_id": str(tax.tax_id.tax_group_id.name_code),
                     "tax_name": str(tax.tax_id.tax_group_id.description),
                     "tax_type_code": str(tax.tax_id.tax_group_id.code)}
            array1.append(dict1)

        line_id = 1
        for line in self.invoice_line_ids:

            TaxTotals = []

            subtotal = line.price_subtotal
            tax_count = 0
            for tax in line.invoice_line_tax_ids.sorted(key=lambda r: r.tax_group_id.sequence):

                taxDict = {
                    "TaxAmount": str(round(subtotal * tax.amount / 100, 2)),
                    "tributo_codigo": str(tax.tax_group_id.code),
                    "tributo_nombre": str(tax.tax_group_id.description),
                    "tributo_tipo_codigo": str(tax.tax_group_id.name_code),
                    "TierRange": "01"
                }
                TaxTotals.append(taxDict)
                subtotal = subtotal * (1 + tax.amount / 100)

            summary_line = BoletaVentaObject.SummaryLine(
                line_id=str(line_id),
                document_type=str(subtotal),
                document_serial="DA45",
                start_document="456",
                end_document="764",
                total_amount="117350.75",
                paid_amount=["78223.00", "24423.00", "0.00"],
                tax_id="01",
                charge_indicator="true",
                amount="0.00",
                array_tax_sub_total=TaxTotals)
                
            line_id = line_id + 1
            Invoice.appendChild(summary_line)

        # Invoice.appendChild(root)
        I = Invoice.toprettyxml("        ")
        self.write({"documentoXML": I})
