#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from utils.Comunicacion import Comunicacion
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

class ComunicacionBaja(models.Model):
    _name = 'account.voided'
    _description = 'Comunicacion de baja'

    number = fields.Char('N° de Comunicación')
    # invoice_date = fields.Date('Fecha documentos', required=True)
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
    motivo = fields.Text(string="Motivo")

    ## Fields from document
    document_date = fields.Date(string="Fecha del documento")
    document_tipo = fields.Selection(string="Tipo de documento",
        selection=[
            ('01', 'Factura'),
            ('03', 'Boleta'),
            ('07', 'Nota de crédito'),
            ('08', 'Nota de débito'),
        ], default='01')
    
    document_serie = fields.Char(string="Serie del documento")
    document_number = fields.Integer(string="Número de documento", help="Colocar el número de documento sin '0' a la izquierda.")

    @api.multi
    def generarComunicacion(self):
        ComunicacionObject = Comunicacion()
        ComunicacionBaja = ComunicacionObject.Root()

        ComunicacionBaja.appendChild(ComunicacionObject.firma(id="placeholder"))

        issue_date = time.strftime('%Y-%m-%d')
        name_issue_date = issue_date.replace('-', '')
        # self.number = 'RC-'+self.invoice_date.replace('-', '')+'-1'
        busqueda = 'RA-'+name_issue_date
        count = self.search([
            ['number', 'like', busqueda+'%']
            ])
        
        if not self.number:
            self.number = 'RA-'+name_issue_date+'-'+str(len(count)+1)
        
        ComunicacionBaja = ComunicacionObject.SummaryRoot(
            rootXML=ComunicacionBaja,
            ubl_version_id='2.0',
            customization_id='1.0',
            summary_id=self.number,
            reference_date=self.document_date,
            issue_date=issue_date
        )
        
        ComunicacionBaja.appendChild(ComunicacionObject.Signature(
			Id="IDSignMT",
			ruc=str(self.company_id.partner_id.vat),
			razon_social=str(self.company_id.partner_id.registration_name),
			uri="#SignatureMT"))
        
        Empresa=ComunicacionObject.cacAccountingSupplierParty(
			num_doc_ident=str(self.company_id.partner_id.vat),
			tipo_doc_ident=str(self.company_id.partner_id.catalog_06_id.code),
			nombre_comercial=self.company_id.partner_id.registration_name)

        ComunicacionBaja.appendChild(Empresa)
        
        # Variable para LineId
        line_id = 1

        SummaryLine = ComunicacionObject.VoidedDocumentsLine(
            line_id=line_id,
            tipo_sunat=self.document_tipo,
            journal=self.document_serie,
            number=self.document_number,
            motivo=self.motivo
        )

        ComunicacionBaja.appendChild(SummaryLine)

        I = ComunicacionBaja.toprettyxml("        ")
        self.write({"documentoXML": I})
        self.firmarResumen()

    @api.multi
    def firmarResumen(self):
        # invoices = self.env['account.invoice']

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

        ComunicacionObject = Comunicacion()
        EnvioXML = ComunicacionObject.sendBill(username=self.company_id.partner_id.vat + self.company_id.sunat_username,
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
        ComunicacionObject = Comunicacion()
        EnvioXML = ComunicacionObject.getStatus(username=self.company_id.partner_id.vat + self.company_id.sunat_username,
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
        os.system("echo 'RESPUESTA:"+r.text+"'")
        try:
            self.documentoRespuestaZip=ET.fromstring(r.text)[0][0][0][0].text
            response_code = ET.fromstring(r.text)[0][0][0][1].text

            if response_code == '0':
                self.state = 'Enviado'
            elif response_code == '98':
                self.state = 'En proceso'
            else:
                self.state = 'Error'
        except Exception, e:
            self.documentoRespuestaZip=""
        self.documentoRespuesta=r.text

        # self.ticket=ET.fromstring(r.text)[0][0][0].text

    @api.multi
    def enviarComunicacion(self):
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