#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from utils.Resumen import Resumen
from signxml import XMLSigner, XMLVerifier,methods
from suds.client import Client
from suds.wsse import *

import xml.etree.ElementTree as ET
import requests
import zipfile
import base64
import os
import requests
import logging
import time
from datetime import datetime,timedelta

class ResumenDiario(models.Model):
    _name = 'account.summary'
    _description = 'Summary BV'

    number = fields.Char('N° de Resumen')
    invoice_date = fields.Date('Fecha boletas')
    documentoXML = fields.Text('Documento XML', default=" ")
    documentoZip = fields.Binary("Documento Zip",default="")
    documentoEnvio = fields.Text("Documento de Envio")
    documentoEnvioTicket = fields.Text("Documento de Envio Ticket")
    paraEnvio = fields.Text("XML para cliente")
    documentoRespuesta = fields.Text("Documento de Respuesta XML")
    documentoRespuestaZip = fields.Binary("Documento de Respuesta ZIP")
    ticket = fields.Char('Ticket respuesta')
    state = fields.Char('Estado', default='Pendiente')

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    @api.model
    def _cron_generarResumenDiario(self):
        obj=self.sudo().create({})

        ResumenDiarioObject = Resumen()
        ResumenDiario = ResumenDiarioObject.Root()

        ResumenDiario.appendChild(ResumenDiarioObject.firma(id="placeholder"))

        issue_date = time.strftime('%Y-%m-%d')

        if obj.invoice_date == False:
            dias = timedelta(days=1)
            reference_date = datetime.now() - dias
            # print reference_date
            obj.invoice_date = reference_date
            reference_date = reference_date.strftime('%Y-%m-%d')
        else:
            reference_date = str(obj.invoice_date)

        # print "Fecha self2: " + str(obj.invoice_date)
        name_issue_date = issue_date.replace('-', '')
        busqueda = 'RC-'+name_issue_date
        count = self.search([
            ['number', 'like', busqueda+'%']
            ])

        if obj.number == False:
            obj.number = 'RC-'+name_issue_date+'-'+str(len(count)+1)

        ResumenDiario = ResumenDiarioObject.SummaryRoot(
            rootXML=ResumenDiario,
            ubl_version_id='2.0',
            customization_id='1.1',
            summary_id=obj.number,
            reference_date = reference_date,
            issue_date=issue_date,
            note='Nota de boletas'
        )

        ResumenDiario.appendChild(ResumenDiarioObject.Signature(
			Id="IDSignMT",
			ruc=str(obj.company_id.partner_id.vat),
			razon_social=str(obj.company_id.partner_id.registration_name),
			uri="#SignatureMT"))

        Empresa=ResumenDiarioObject.cacAccountingSupplierParty(
			num_doc_ident=str(obj.company_id.partner_id.vat),
			tipo_doc_ident=str(obj.company_id.partner_id.catalog_06_id.code),
			nombre_comercial=obj.company_id.partner_id.registration_name,
			codigo_ubigeo=str(obj.company_id.partner_id.zip),
			nombre_direccion_full=str(obj.company_id.partner_id.street),
			nombre_direccion_division=obj.company_id.partner_id.street2,
			nombre_departamento=str(obj.company_id.partner_id.state_id.name),
			nombre_provincia=str(obj.company_id.partner_id.province_id.name),
			nombre_distrito=str(obj.company_id.partner_id.district_id.name),
			nombre_proveedor=str(obj.company_id.partner_id.registration_name),
			codigo_pais="PE")

        ResumenDiario.appendChild(Empresa)

        # Seleccionamos los diarios de Boleta de venta
        # 03 => Boleta de venta
        # 07 => Nota de crédito
        # 08 => Nota de débito
        journals_code = self.env['account.journal'].search([
            ['invoice_type_code_id', 'in', ['03', '07', '08']],
            ['code', 'not like', 'F']
            ])

        # Variable para LineId
        line_id = 1

        # Recorremos el arreglo
        for journal in journals_code:
            # Obtenemos las boletas del dia
            boleta_ids = self.env['account.invoice'].search([
                ['state','in',['open', 'paid']],
                ['date_invoice', '=', str(reference_date)],
                ['journal_id.code', '=', journal.code]
                ],order="number asc")

            # Si tenemos boletas dentro del arreglo
            if boleta_ids:
                # Recorremos el array de boletas de venta
                for boleta in boleta_ids:
                    if boleta.number != 'BC01-00000025':
                        if boleta.invoice_type_code == '07':
                            origen = boleta.origin
                        else:
                            origen = False

                        SummaryLine = ResumenDiarioObject.SummaryDocumentsLine(
                            line_id=line_id,
                            number=boleta.number,
                            ruc=boleta.partner_id.vat,
                            tipo_doc=boleta.partner_id.catalog_06_id.code,
                            tipo_sunat=boleta.invoice_type_code,
                            origen=origen,
                            gravado=boleta.total_venta_gravado,
                            inafecto=boleta.total_venta_inafecto,
                            exonerada=boleta.total_venta_exonerada,
                            amount_tax=boleta.amount_tax)

                        ResumenDiario.appendChild(SummaryLine)
                        line_id = line_id +1

        if line_id > 1:
            I = ResumenDiario.toprettyxml("        ")
            obj.write({"documentoXML": I})
            obj.firmarResumen()
            obj.enviarResumen()

    def tipodocumento_proccess(self):
        journals_code = self.env['account.journal'].search([
            ['invoice_type_code_id', 'in', ['03']],
            ['code', 'not like', 'F']
            ])

        for journal in journals_code:
            # Obtenemos las boletas del dia
            boleta_ids = self.env['account.invoice'].search([
                ['state','in',['open', 'paid']],
                ['journal_id.code', '=', journal.code]
                ],order="number asc")
            # Si tenemos boletas dentro del arreglo
            if boleta_ids:
                # Recorremos el array de boletas de venta
                for boleta in boleta_ids:
                    boleta.invoice_type_code = '03'

    @api.multi
    def generarResumenDiario(self):
        ResumenDiarioObject = Resumen()
        ResumenDiario = ResumenDiarioObject.Root()

        ResumenDiario.appendChild(ResumenDiarioObject.firma(id="placeholder"))

        issue_date = time.strftime('%Y-%m-%d')

        if self.invoice_date == False:
            dias = timedelta(days=1)
            reference_date = datetime.now() - dias
            # self.invoice_date = reference_date
            # print reference_date
            reference_date = reference_date.strftime('%Y-%m-%d')
            #self.invoice_date = reference_date
        else:
            reference_date = str(self.invoice_date)

        # print "Fecha self2: " + str(self.invoice_date)
        name_issue_date = issue_date.replace('-', '')
        busqueda = 'RC-'+name_issue_date
        count = self.search([
            ['number', 'like', busqueda+'%']
            ])

        if self.number == False:
            self.number = 'RC-'+name_issue_date+'-'+str(len(count)+1)

        ResumenDiario = ResumenDiarioObject.SummaryRoot(
            rootXML=ResumenDiario,
            ubl_version_id='2.0',
            customization_id='1.1',
            summary_id=self.number,
            reference_date = reference_date,
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
        # 03 => Boleta de venta
        # 07 => Nota de crédito
        # 08 => Nota de débito
        journals_code = self.env['account.journal'].search([
            ['invoice_type_code_id', 'in', ['03', '07', '08']],
            ['code', 'not like', 'F']
            ])

        # Variable para LineId
        line_id = 1

        # Recorremos el arreglo
        for journal in journals_code:
            # Obtenemos las boletas del dia
            boleta_ids = self.env['account.invoice'].search([
                ['state','in',['open', 'paid']],
                ['date_invoice', '=', str(reference_date)],
                ['journal_id.code', '=', journal.code]
                ],order="number asc")
            
            # Si tenemos boletas dentro del arreglo
            if boleta_ids:
                # Recorremos el array de boletas de venta
                print("BOLETAS DE VENTA")
                print(boleta_ids)
                for boleta in boleta_ids:
                    origin_number = self.env['account.invoice'].search([
                        ['number', '=', boleta.origin]
                        ])
                    if boleta.invoice_type_code == '07' and origin_number.invoice_type_code == '03':
                        origen = boleta.origin
                        SummaryLine = ResumenDiarioObject.SummaryDocumentsLine(
                        line_id=line_id,
                        number=boleta.number,
                        ruc=boleta.partner_id.vat,
                        tipo_doc=boleta.partner_id.catalog_06_id.code,
                        tipo_sunat=boleta.invoice_type_code,
                        origen=origen,
                        gravado=boleta.total_venta_gravado,
                        inafecto=boleta.total_venta_inafecto,
                        exonerada=boleta.total_venta_exonerada,
                        amount_tax=boleta.amount_tax)

                        ResumenDiario.appendChild(SummaryLine)
                        line_id = line_id +1
                    elif boleta.invoice_type_code == '03':
                        origen = False
                        print('NUMERO DE BOLETA')
                        print(boleta.number)

                        SummaryLine = ResumenDiarioObject.SummaryDocumentsLine(
                        line_id=line_id,
                        number=boleta.number,
                        ruc=boleta.partner_id.vat,
                        tipo_doc=boleta.partner_id.catalog_06_id.code,
                        tipo_sunat=boleta.invoice_type_code,
                        origen=origen,
                        gravado=boleta.total_venta_gravado,
                        inafecto=boleta.total_venta_inafecto,
                        exonerada=boleta.total_venta_exonerada,
                        amount_tax=boleta.amount_tax)

                        ResumenDiario.appendChild(SummaryLine)
                        line_id = line_id +1

        if line_id > 1:
            I = ResumenDiario.toprettyxml("        ")
            self.write({"documentoXML": I})
            self.firmarResumen()

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
        name_file=self.company_id.partner_id.vat+"-"+self.number
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

        ResumenObject = Resumen()
        EnvioXML = ResumenObject.sendBill(username=self.company_id.partner_id.vat + self.company_id.sunat_username,
                               password=self.company_id.sunat_password,
                               namefile=name_file+".zip",
                               contentfile=self.documentoZip)
        self.documentoEnvio=EnvioXML.toprettyxml("        ")
        # ResumenObject = Resumen()
        # EnvioXML = ResumenObject.getStatus(username=self.company_id.partner_id.vat + self.company_id.sunat_username,
        #                        password=self.company_id.sunat_password,
        #                        namefile=name_file+".zip",
        #                        contentfile=self.documentoZip)
        # self.documentoEnvio=EnvioXML.toprettyxml("        ")

    @api.multi
    def estadoTicket(self):
        ResumenObject = Resumen()
        EnvioXML = ResumenObject.getStatus(username=self.company_id.partner_id.vat + self.company_id.sunat_username,
                               password=self.company_id.sunat_password,
                               ticket_r=self.ticket)
        self.documentoEnvioTicket=EnvioXML.toprettyxml("        ")
        self.enviarTicket()

    @api.multi
    def enviarTicket(self):
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
                        data=self.documentoEnvioTicket,
                        headers={"Content-Type":"text/xml"})
        # os.system("echo 'RESPUESTA:"+r.text+"'")
        try:
            self.documentoRespuestaZip=ET.fromstring(r.text)[0][0][0][0].text
            response_code = ET.fromstring(r.text)[0][0][0][1].text

            if response_code == '0':
                self.state = 'Enviado'
            elif response_code == '0098':
                self.state = 'En proceso'
            else:
                self.state = 'Error'
        except Exception, e:
            self.documentoRespuestaZip=""
        self.documentoRespuesta=r.text

        # self.ticket=ET.fromstring(r.text)[0][0][0].text

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
        # try:
        #     self.documentoRespuestaZip=ET.fromstring(r.text)[0][0][0][0].text
        # except Exception, e:
        #     self.documentoRespuestaZip=""
        self.documentoRespuesta=r.text

        self.ticket=ET.fromstring(r.text)[1][0][0].text

        self.estadoTicket()