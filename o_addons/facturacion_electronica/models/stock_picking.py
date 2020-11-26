#!/usr/bin/env python
# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.http import request
from odoo.tools.float_utils import float_compare
'''from .InvoiceLine import Factura  #utils
from .NotaCredito import NotaCredito
from .NotaDebito import NotaDebito
from . import utils
from utils import InvoiceLine as Factura 
from utils import NotaCredito as NotaCredito
from utils import NotaDebito as NotaDebito'''
from . import Factura  #
from . import NotaCredito
from . import NotaDebito
from . import GuiaRemision
#https://stackoverflow.com/questions/16780510/module-object-is-not-callable-calling-method-in-another-file/16780543
from suds.client import Client  #para exportar y la firma 
from suds.wsse import * #para exportar y la firmaa
from signxml import XMLSigner, XMLVerifier, methods  #para exportar y la firmaa
from datetime import datetime, timedelta
#from io import StringIO
#import io
from cStringIO import StringIO
import xlwt, xlsxwriter
from xlwt import easyxf
import xml.etree.ElementTree as ET
import requests
import zipfile
import base64

import os
import logging
import json
import math
import time
import calendar
#import unicodedata
'''import sys 
sys.path.insert(0, 'utils/InvoiceLine')
sys.path.insert(0, 'utils/NotaCredito')
sys.path.insert(0, 'utils/NotaDebito')'''

# mapping invoice type to refund type
TYPE2REFUND = {
    "out_invoice": "out_refund",  # Customer Invoice
    "in_invoice": "in_refund",  # Vendor Bill
    "out_refund": "out_invoice",  # Customer Refund
    "in_refund": "in_invoice",  # Vendor Refund
}

'''
class ActivosFijos(models.Model):
    _name = "account.activos"

    codigo = fields.Text("Código")
    descripcion = fields.Text("Descripción")
    marca = fields.Text("Marca de activo fijo")
    modelo = fields.Text("Modelo del activo fijo")
    serie = fields.Text("Número de serie y/o placa del activo fijo")
    saldo = fields.Float("Saldo inicial")
    adquisicion = fields.Text("Adquisiciones")
    mejora = fields.Text("Mejoras")
    retiro = fields.Text("Retiros y/o bajas")
    otros = fields.Text("Otros ajustes")
    historico = fields.Text("Valor histórico")
    inflacion = fields.Text("Ajuste por inflación")
    ajustado = fields.Text("Valor ajustado")
    fecha_adq = fields.Date("Fecha de adquisición")
    fecha_uso = fields.Date("Fecha de inicio de uso")
    metodo = fields.Text("Método aplicado")
    n_documento = fields.Text("Nro. de documento de autorización")
    porcentaje = fields.Float("Porcentaje de depreciación")
    acumulada = fields.Text("Depreciación acumulada al cierre del ejercicio anterior")
    depreciacion = fields.Text("Depreciación del ejercicio")
    depreciacion_retiro = fields.Text(
        "Depreciación  del ejercicio relacionada con retiros y/o bajas"
    )
    depreciacion_otros = fields.Text("Depreciación relacionada con otros ajustes")
    depreciacion_acumulada = fields.Text("Depreciación acumulada histórica")
    depreciacion_ajuste = fields.Text("Ajuste por inflación de la depreciación")
    depreciacion_acumulada_ajustada = fields.Text(
        "Depreciación acumulada ajustada por inflación"
    )
'''

class StockPicking(models.Model):
    _inherit = "stock.picking"

    pruebautils = fields.Text("utils", copy=False)
    documentoXML = fields.Text("Documento XML", default=" ", copy=False)
    documentoXMLcliente = fields.Binary("XML cliente", copy=False)
    documentoXMLcliente_fname = fields.Char(
        "Prueba name", compute="set_xml_filename", copy=False
    )
    documentoZip = fields.Binary("Documento Zip", default="", copy=False)
    documentoEnvio = fields.Text("Documento de Envio", copy=False)
    paraEnvio = fields.Text("XML para cliente", copy=False)
    documentoRespuesta = fields.Text("Documento de Respuesta XML", copy=False)
    documentoRespuestaZip = fields.Binary("CDR SUNAT", copy=False)
    documentoEnvioTicket = fields.Text("Documento de Envio Ticket", copy=False)
    numeracion = fields.Char("Número de factura", copy=False)
    mensajeSUNAT = fields.Char("Respuesta SUNAT", copy=False)
    codigoretorno = fields.Char("Código retorno", default="0000", copy=False)
    estado_envio = fields.Boolean("Enviado a SUNAT", default=False, copy=False)
    operacionTipo = fields.Selection(
        string="Tipo de operación",
        selection=[
            ("0101", "Venta interna"),
            ("0200", "Exportación de bienes"),
            ("0401", "Ventas no domiciliados que no califican como exportación"),
        ],
        default="0101",
    )
    type = fields.Selection(
        string="Type",
        selection=[
            ("out_invoice", "Factura de Cliente"),
            ("in_invoice", "Factura de Proveedor"),
            ("out_refund", "Rectificativa de cliente "),
            ("in_refund", "Rectificativa de Proveedor"),
        ],
        default="out_invoice",
    )

    # invoice_type_code = fields.Selection(string="Tipo de Comprobante", store=True, related="journal_id.invoice_type_code_id", readonly=True)
    # invoice_type_code = fields.Char(string="Tipo de Comprobante", default=_set_invoice_type_code, readonly = True)

    # Para documentos de proveedor
    def _list_invoice_type(self):
        catalogs = self.env["einvoice.catalog.01"].search([])
        list = []
        for cat in catalogs:
            list.append((cat.code, cat.name))
        return list

    tipo_documento = fields.Selection(
        string="Tipo de Documento", selection=_list_invoice_type, default="09"
    )
    muestra = fields.Boolean("Muestra", default=False)
    send_route = fields.Selection(
        string="Ruta de envío", store=True, related="company_id.send_route", readonly=True
    )

    response_code = fields.Char("response_code", copy=False)
    referenceID = fields.Char("Referencia", copy=False)
    motivo = fields.Text("Motivo")

    """total_venta_gravado = fields.Monetary(
        "Gravado", default=0.0
    )#, compute="_compute_total_venta"
    total_venta_inafecto = fields.Monetary(
        "Inafecto", default=0.0
    )#, compute="_compute_total_venta"
    total_venta_exonerada = fields.Monetary(
        "Exonerado", default=0.0
    )#, compute="_compute_total_venta"
    total_venta_gratuito = fields.Monetary(
        "Gratuita", default=0.0
    )#, compute="_compute_total_venta"
    total_descuentos = fields.Monetary(
        "Total Descuentos", default=0.0
    )#, compute="_compute_total_venta" """ 
    type_code = fields.Char(string="Tipo de Comprobante", default="09")#
    journal_id=fields.Many2one("account.journal",string="Diario",domain="[('invoice_type_code_id','=','09')]")#domain="[('invoice_type_code_id','=',type_code)]" 31remision guia de transporte

    digestvalue = fields.Char("DigestValue")
    final = fields.Boolean("Es final?", default=False, copy=False)

    # @api.one
    # def _set_invoice_type_code(self):
    #     prueba = self.journal_id.invoice_type_code_id
    #     return prueba 

    invoice_type_code = fields.Char(string="Tipo de Comprobante", default="09")
    move_id = fields.Many2one('stock.move', string='Journal Entry',
        readonly=True, index=True, ondelete='restrict', copy=False,
        help="Link to the automatically generated Journal Items.")

    number = fields.Char(related='move_id.name', store=True, readonly=True, copy=False)

    def set_xml_filename(self):
        lis_numer=str(self.name).split("/")
        nombre='-'.join(lis_numer)
        #self.documentoXMLcliente_fname = str(self.number) + ".xml"
        self.documentoXMLcliente_fname = str(nombre) + ".xml"

    def _compute_zip(self):
        self.documentoRespuestaZip = ET.fromstring(str(self.documentoRespuesta))[1][0][
            0
        ].text

    def _compute_number_begin(self):
        if self.number:
            if "F" in self.number:
                return True
            else:
                return False

    ## MODIFICACIONES DANIEL
    def enviar_correo(self):
        template = self.env.ref("account.email_template_edi_invoice", False)
        mail_id = self.env["mail.template"].sudo().browse(template.id).send_mail(self.id)
        mail = self.env["mail.mail"].sudo().browse(mail_id)
        mail.send()

    ## MODIFICACION DANIEL

    def _list_reference_code_credito(self):
        catalogs = self.env["einvoice.catalog.09"].search([])
        list = []
        for cat in catalogs:
            list.append((cat.code, cat.name))
        return list

    def _list_reference_code_debito(self):
        catalogs = self.env["einvoice.catalog.10"].search([])
        list = []
        for cat in catalogs:
            list.append((cat.code, cat.name))
        return list

    response_code_credito = fields.Selection(
        string="Código de motivo", selection=_list_reference_code_credito
    )
    response_code_debito = fields.Selection(
        string="Código de motivo", selection=_list_reference_code_debito
    )
    ##################################### 
    ###################################### 
    @api.model
    def _prepare_refund(
        self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
    
        """ Prepare the dict of values to create the new refund from the invoice.
            This method may be overridden to implement custom
            refund generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice to refund
            :param string date_invoice: refund creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the refund from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the refund
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == "many2one":
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values["invoice_line_ids"] = self._refund_cleanup_lines(invoice.invoice_line_ids)

        tax_lines = invoice.tax_line_ids
        values["tax_line_ids"] = self._refund_cleanup_lines(tax_lines)

        if journal_id:
            journal = self.env["account.journal"].browse(journal_id)
        elif invoice["type"] == "in_invoice":
            journal = self.env["account.journal"].search(
                [("type", "=", "purchase")], limit=1
            )
        else:
            journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        values["journal_id"] = journal.id

        values["type"] = TYPE2REFUND[invoice["type"]]
        values["date_invoice"] = date_invoice or fields.Date.context_today(invoice)
        values["state"] = "draft"
        values["number"] = False
        values["origin"] = invoice.number
        values["payment_term_id"] = False
        values["refund_invoice_id"] = invoice.id
        values["invoice_type_code"] = "09"

        if date:
            values["date"] = date
        if description:
            values["name"] = description
        return values

    @api.multi
    @api.returns("self")
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        new_invoices = self.browse()
        for invoice in self:
            # create the new invoice
            values = self._prepare_refund(
                invoice,
                date_invoice=date_invoice,
                date=date,
                description=description,
                journal_id=journal_id,
            )
            refund_invoice = self.create(values)
            invoice_type = {
                "out_invoice": ("customer invoices refund"),
                "in_invoice": ("vendor bill refund"),
            }
            message = _(
                "This %s has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>"
            ) % (invoice_type[invoice.type], invoice.id, invoice.number)
            refund_invoice.message_post(body=message)
            new_invoices += refund_invoice
        return new_invoices

    def _get_refund_modify_read_fields(self):
        read_fields = [
            "type",
            "number",
            "invoice_line_ids",
            "tax_line_ids",
            "date",
            "invoice_type_code",
        ]
        return (
            self._get_refund_common_fields()
            + self._get_refund_prepare_fields()
            + read_fields
        )

    #########################
    ########################
    #######################

    @api.model
    def default_get(self, fields_list):
        res = super(StockPicking, self).default_get(fields_list)

        journal_id = self.env["account.journal"].search(
            [["invoice_type_code_id", "=",'09']], limit=1
        )#self._context.get("type_code")
        res["journal_id"] = journal_id.id
        return res

    @api.one
    @api.depends(
        "invoice_line_ids.price_subtotal",
        "tax_line_ids.amount",
        "currency_id",
        "company_id",
        "date_invoice",
        "type",
    )
    
    @api.multi
    def firmar(self):  #hace la firma
        #data_unsigned = ET.fromstring(self.documentoXML.encode("utf-8").strip()) 
        data_unsigned = ET.fromstring(self.documentoXML.encode("utf-8").strip())
        #ET.tostring(signed_root).decode("utf-8")
        #xml_file = xml_file.encode("utf-8")
        #self.documentoXMLcliente = base64.b64encode(xml_file)
        #
        
        namespaces = {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "ccts": "urn:un:unece:uncefact:documentation:2",
            "ds": "http://www.w3.org/2000/09/xmldsig#",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2",
            "sac": "urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1",
            "udt": "urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }#
        

        if self.invoice_type_code == "01" or self.invoice_type_code == "03":
            if self.type == "out_invoice":
                namespaces.update(
                    {"": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"}
                )
            elif self.type == "out_refund":
                namespaces.update(
                    {"": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"}
                )
        elif self.invoice_type_code == "09":
            namespaces.update(
                {"": "urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"}
            )
        elif self.invoice_type_code == "07":
            namespaces.update(
                {"": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"}
            )
        elif self.invoice_type_code == "08":
            namespaces.update(
                {"": "urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2"}
            )
        else : 
            if self.type == "out_invoice":
                namespaces.update(
                    {"": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"}
                )
            elif self.type == "out_refund":
                namespaces.update(
                    {"": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"}
                )

        #
        for prefix, uri in namespaces.items():#iteritems  items viewitems
            ET.register_namespace(prefix, uri) #no esta funcionando 
            #ET._namespace_map[uri] = prefix
            #ET.register_namespace("20521467984-False-FV/2020/0032.xml", "/var/lib/odoo/")#20521467984-False-FV/2020/0032.xml

        uri = "/var/lib/odoo/"  #
        
        lis_numer=str(self.name).split("/")
        nombre='-'.join(lis_numer)
        name_file = (
            self.company_id.partner_id.vat
            + "-" + str(self.invoice_type_code) + "-" + str(nombre)
        )
        #+ "-" + str(self.invoice_type_code) + "-" + str(self.number)
        #+ str(lis_numer[2]) 
        file = open(uri + name_file + ".xml", "w")#name_file=20521467984-31-WH/OUT/00026.xml  + name_file  

        signed_root = XMLSigner(
            method=methods.enveloped,
            digest_algorithm="sha1",
            c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
        ).sign(
            data_unsigned,
            key=str(self.company_id.private),
            cert=str(self.company_id.public),
        )

        signed_root[0][0][0][0].set("Id", "SignatureMT")

        self.digestvalue = signed_root[0][0][0][0][0][2][2].text
        #element = ET.fromstring(signed_root)  
        #file.write(tostring(element))#str(ET.tostring(signed_root))  ET.tostring(signed_root)
        file.write(ET.tostring(signed_root).decode("utf-8"))
        file.close()

        xfile = open(uri + name_file + ".xml", "r")
        xml_file = xfile.read()
        xml_file = xml_file.encode("utf-8")
        self.documentoXMLcliente = base64.b64encode(xml_file) #str(xml_file) 
        xfile.close()

        zf = zipfile.ZipFile(uri + name_file + ".zip", mode="w")
        '''try:
            zf.write(uri + name_file + ".xml", arcname=name_file + ".xml")
        except Exception, e:
            zf.close()'''
        zf.close()

        f = open(uri + name_file + ".zip", "rb")
        data_file = f.read()
        #data_file = data_file.encode("utf-8") 
        self.documentoZip = base64.b64encode(data_file) #str(data_file)
        self.documentoXML = ET.tostring(signed_root)

        f.close()

        FacturaObject = Factura.Factura()
        EnvioXML = FacturaObject.sendBill(
            username=self.company_id.partner_id.vat + self.company_id.sunat_username,
            password=self.company_id.sunat_password,
            namefile=name_file + ".zip",
            contentfile=str(self.documentoZip),
        )
        self.documentoEnvio = EnvioXML.toprettyxml("        ")

    @api.multi
    def enviar(self):
        url = self.company_id.send_route

        r = requests.post(
            url=url,
            data=self.documentoEnvio,
            headers={"Content-Type": "text/xml"},
            verify=False,
        )

        '''try:
            self.documentoRespuestaZip = ET.fromstring(r.text)[0][0][0].text
        except Exception, e:
            self.documentoRespuestaZip = "" '''

        self.documentoRespuesta = r.text

    @api.multi
    def descargarRespuesta(self):
        name_file = (
            "R-"
            + self.company_id.partner_id.vat
            + "-"
            + str(self.journal_id.invoice_type_code_id)
            + "-"
            + str(self.number)
        )
        url = self.env["ir.config_parameter"].search([["key", "=", "web.base.url"]])[
            "value"
        ]
        file_url = (
            url
            + "/web/content/account.invoice/"
            + str(self.id)
            + "/documentoRespuestaZip/"
            + name_file
            + ".zip"
        )
        return {"type": "ir.actions.act_url", "url": file_url, "target": "new"}

    # Llamar desde cronjob para pasar number ==> numeracion
    def number_to_numeracion(self):
        facturas = self.search([])
        for f in facturas:
            f.numeracion = f.number

    # Llamar desde cronjob para realizar consulta masiva a SUNAT
    def _envio_masivo(self):
        facturas = self.search(
            [
                ["codigoretorno", "=", False],
                ["state", "in", ["open", "paid"]],
                ["journal_id.invoice_type_code_id", "=", "09"],
            ]
        )
        for f in facturas:
            FacturaObject = Factura.Factura()
            EnvioXML = FacturaObject.getStatus(
                username=str(f.company_id.sunat_username),
                password=str(f.company_id.sunat_password),
                ruc=str(f.company_id.partner_id.vat),
                tipo=str(f.invoice_type_code),
                numero=f.number,
            )
            f.documentoEnvioTicket = EnvioXML.toprettyxml("        ")

            url = "https://www.sunat.gob.pe/ol-it-wsconscpegem/billConsultService"

            r = requests.post(
                url=url, data=f.documentoEnvioTicket, headers={"Content-Type": "text/xml"}
            )

            f.mensajeSUNAT = ET.fromstring(r.text.encode("utf-8"))[0][0][0][1].text
            f.codigoretorno = ET.fromstring(r.text.encode("utf-8"))[0][0][0][0].text

            if f.codigoretorno in ("0001", "0002", "0003"):
                f.estado_envio = True

    # Genera XML para consulta a SUNAT
    @api.multi
    def estadoTicket(self):
        FacturaObject = Factura.Factura()
        EnvioXML = FacturaObject.getStatus(
            username=str(self.company_id.sunat_username),
            password=str(self.company_id.sunat_password),
            ruc=str(self.company_id.partner_id.vat),
            tipo=str(self.invoice_type_code),
            numero=self.number,
        )
        self.documentoEnvioTicket = EnvioXML.toprettyxml("        ")
        self.enviarTicket()

    # Envia consulta a SUNAT
    @api.multi
    def enviarTicket(self):
        url = "https://www.sunat.gob.pe/ol-it-wsconscpegem/billConsultService"

        r = requests.post(
            url=url,
            data=self.documentoEnvioTicket,
            headers={"Content-Type": "text/xml"},
            verify=False,
        )

        self.mensajeSUNAT = ET.fromstring(r.text.encode("utf-8"))[0][0][0][1].text
        self.codigoretorno = ET.fromstring(r.text.encode("utf-8"))[0][0][0][0].text

        if self.codigoretorno in ("0001", "0002", "0003"):
            self.estado_envio = True

    @api.one
    def button_validate(self):
        ''' Herencia de metodo original de validacion de facturas.'''
        #to_open_invoices = self.filtered(lambda inv: inv.state != "done")
        
        res = super(StockPicking, self).button_validate()
        #if self.invoice_type_code == "09":
        self.generarGuiaRemision()#
        self.firmar()
        #response =to_open_invoices.button_validate()
        return res

    @api.one
    def do_new_transfer(self):
        ''' Herencia de metodo original de validacion de facturas.'''
        #to_open_invoices = self.filtered(lambda inv: inv.state != "done")
        
        res = super(StockPicking, self).do_new_transfer()
        #if self.invoice_type_code == "09":
        self.generarGuiaRemision()#
        self.firmar()
        #response =to_open_invoices.button_validate()
        return res

    def elimina_tildes(self,cadena):
        s = ''.join((c for c in unicodedata.normalize('NFD',cadena) if unicodedata.category(c) != 'Mn'))
        return s
    # Validacion de documento 
    @api.multi
    def action_invoice_open(self):

        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != "open")
        if to_open_invoices.filtered(lambda inv: inv.state not in ["proforma2", "draft"]):
            raise UserError(
                _("Invoice must be in draft or Pro-forma state in order to validate it.")
            )
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()

        if self.type == "out_refund":
            self.invoice_type_code = "07"
        else:
            self.invoice_type_code = self.journal_id.invoice_type_code_id

        if self.journal_id.invoice_type_code_id:
            if self.invoice_type_code in ("01", "03"):
                if self.type == "out_invoice":
                    self.generarFactura()
                elif self.type == "out_refund":
                    self.generarNotaCredito()
            elif self.invoice_type_code == "07":
                self.generarNotaCredito()
            elif self.invoice_type_code == "08":
                self.generarNotaDebito()
            elif self.invoice_type_code == "09":
                self.generarGuiaRemision()

            self.firmar()

        response = to_open_invoices.invoice_validate()

        self.numeracion = self.number
        return response

    @api.multi
    def generarGuiaRemision(self):  #generar xml
        #ico = self.incoterms_id 
        fecha_hora=(self.min_date).split(" ")
        if self.note == False:
            note_descripcion = '-'
        FacturaObject = GuiaRemision.GuiaRemision()
        Invoice = FacturaObject.Root()
        Invoice.appendChild(FacturaObject.UBLExtensions())
        Invoice = FacturaObject.InvoiceRoot(
            rootXML=Invoice,
            versionid="2.1",
            customizationid="2.0",
            id=str(self.name),#Numeracion, conformada por serie y Número correlativo
            issuedate=str(fecha_hora[0]),#fecha emision
            issuetime=str(fecha_hora[1]),#hora de emision
            operacion=self.operacionTipo,
            invoicetypecode=str(self.journal_id.invoice_type_code_id),
            documentcurrencycode=str(self.journal_id.invoice_type_code_id),
            note=str(note_descripcion),#observacion maximo 250
        )
       
        OrderReference = FacturaObject.cacOrderReference(
            documento=self.name,
            num_doc_ident=str(self.company_id.partner_id.vat),
            tipo_doc_ident=str(
                self.company_id.partner_id.catalog_06_id.code
            ),
        )
        Invoice.appendChild(OrderReference)
        #falta Agregar
        additional = FacturaObject.cacAdditionalDocumentReference(
            documento=self.origin,#Número de documento del documento relacionado
            num_doc_ident=str(self.company_id.partner_id.vat),
            tipo_doc_ident=str(
                self.company_id.partner_id.catalog_06_id.code
            ),
        )
        Invoice.appendChild(additional)

        nom_compania = self.company_id.partner_id.registration_name
        if nom_compania == False:
            nom_compania = self.company_id.partner_id.name

        Empresa = FacturaObject.cacAccountingSupplierParty(
            num_doc_ident=str(self.company_id.partner_id.vat),
            tipo_doc_ident=str(self.company_id.partner_id.catalog_06_id.code),
            nombre_comercial=str(nom_compania),
            codigo_ubigeo=str(self.company_id.partner_id.zip),
            nombre_direccion_full=str(self.company_id.partner_id.street),
            nombre_direccion_division=self.company_id.partner_id.street2,
            nombre_departamento=str(self.company_id.partner_id.state_id.name),
            nombre_provincia=str(self.company_id.partner_id.province_id.name),
            nombre_distrito=str(self.company_id.partner_id.district_id.name),
            nombre_proveedor=str(self.company_id.partner_id.registration_name),
            codigo_pais="PE",
        )

        Invoice.appendChild(Empresa)

        # DOCUMENTO DE IDENTIDAD
        num_doc_ident = str(self.partner_id.vat)
        if num_doc_ident == "False":
            num_doc_ident = "-"

        parent = self.partner_id.parent_id
        if parent:
            doc_code = str(self.partner_id.parent_id.catalog_06_id.code)
            nom_cli = self.partner_id.parent_id.registration_name
            if nom_cli == False:
                nom_cli = self.partner_id.parent_id.name
        else:
            doc_code = str(self.partner_id.catalog_06_id.code)
            nom_cli = self.partner_id.registration_name
            if nom_cli == False:
                nom_cli = self.partner_id.name
        if self.picking_type_id.code=='outgoing':  #clientes
            Cliente = FacturaObject.cacAccountingCustomerParty(
                num_doc_identidad=num_doc_ident,
                tipo_doc_identidad=doc_code,
                nombre_cliente=nom_cli,
            )
            Invoice.appendChild(Cliente)

        #Proveedor
        if self.picking_type_id.code=='incoming' :  #proveedor
            Seller = FacturaObject.cacSellerSupplierParty(
                num_doc_ident=num_doc_ident,
                tipo_doc_ident=doc_code,
                nombre_comercial=nom_cli,#
            
            )

            Invoice.appendChild(Seller)

        #Transportista 
        #falta agregar compañia
        partner_id_street = self.partner_id.street
        if partner_id_street == False:
            partner_id_street = ' '
        partner_id_street2 = self.partner_id.street2
        if partner_id_street2 == False:
            partner_id_street2 = ' '
        partner_id_city = self.partner_id.city
        if partner_id_city == False:
            partner_id_city = ' '
        partner_id_state_id_name = self.partner_id.state_id.name
        if partner_id_state_id_name == False:
            partner_id_state_id_name = ' '
        partner_id_country_id = self.partner_id.country_id.name
        if partner_id_country_id == False:
            partner_id_country_id = 'Peru'
        #trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
        #s = unicodedata.normalize('NFKC', unicodedata.normalize('NFKD', s).translate(trans_tab))

        if self.picking_type_id.code=='incoming' :  #proveedor
            direccion_punto_llegada=str(self.company_id.partner_id.street)+' '+str(self.company_id.partner_id.street2)+' '+str(self.company_id.partner_id.city)+' '+str(self.company_id.partner_id.state_id.name)+' '+str(self.company_id.partner_id.country_id.name)
            direccion_punto_partida=str(partner_id_street)+' '+str(partner_id_street2)+' '+str(partner_id_city)+' '+str(partner_id_state_id_name)+' '+str(partner_id_country_id)
            ubigeo_punto_partida=self.partner_id.state_id.code
            ubigeo_punto_llegada=self.company_id.state_id.code
        elif self.picking_type_id.code=='outgoing' : #cliente
            direccion_punto_llegada=str(partner_id_street)+' '+str(partner_id_street2)+' '+str(partner_id_city)+' '+str(partner_id_state_id_name)+' '+partner_id_country_id
            direccion_punto_partida=str(self.company_id.partner_id.street)+' '+str(self.company_id.partner_id.street2)+' '+str(self.company_id.partner_id.city)+' '+str(self.company_id.partner_id.state_id.name)+' '+self.company_id.partner_id.country_id.name#falta
            ubigeo_punto_partida=self.company_id.state_id.code
            ubigeo_punto_llegada=self.partner_id.state_id.code
        else:
            direccion_punto_llegada=str(partner_id_street)+' '+str(partner_id_street2)+' '+str(partner_id_city)+' '+str(partner_id_state_id_name)+' '+str(partner_id_country_id)
            direccion_punto_partida=str(self.company_id.partner_id.street)+' '+str(self.company_id.partner_id.street2)+' '+str(self.company_id.partner_id.city)+' '+str(self.company_id.partner_id.state_id.name)+' '+str(self.company_id.partner_id.country_id.name)
            ubigeo_punto_partida=self.company_id.state_id.code
            ubigeo_punto_llegada=self.partner_id.state_id.code
        datos=self.env["stock.picking"].search([["origin", "=", self.origin]])
        Transportista = FacturaObject.cacShipment(
            ruc_trans=str(datos.transportista.parent_id.vat),
            tipo_doc_identidad_trans=str(datos.transportista.parent_id.catalog_06_id.code),
            razon_social=str(datos.transportista.parent_id.registration_name),#empresa que pertenece el conductor
            placa_vehiculo=str(datos.transportista.vehiculo.licence_plate),#
            dni_conductor=str(datos.transportista.vat),
            tipo_doc_identidad_cond=str(datos.transportista.catalog_06_id.code),
            motivo_traslado=str(datos.motivo_traslado.name),
            descrip_motiv_traslado=str(datos.descripcion_motivo_traslado), 
            indicador_transbordo=str(datos.Indicador_de_transbordo),
            peso_bruto_total=str(datos.weight),
            unidad_medida_peso=str(datos.weight_uom_id),
            numero_de_bulto=str(datos.number_of_packages),
            modalidad_traslado=datos.modalidad_traslado.name,#tilde falla
            fecha_inicio_traslado=str(datos.transport_date),
            ubigeo_punto_partida=str(ubigeo_punto_partida),
            direccion_punto_partida=direccion_punto_partida,#
            ubigeo_punto_llegada=str(ubigeo_punto_llegada),#del cliente
            direccion_punto_llegada=direccion_punto_llegada,#del cliente
            codigo_puerto_embarque=str(datos.puerto_embar.name),
            codigo_puerto_desembarque=str(datos.puerto_desembar.name),
            codigo_contenedor=str(datos.contenedor.name)
        )
        Invoice.appendChild(Transportista)
        if self.final:
            facturas = (
                self.env["sale.order"].search([["name", "=", self.origin]]).invoice_ids
            )
            for f in facturas:
                if f.state in ("open", "paid"):
                    if f.number != self.number:
                        # print('FACTURA DE ORDEN DE VENTA', f.number)
                        prepaid = FacturaObject.cacPrepaidPayment(
                            currency=f.currency_id.name,
                            monto=f.amount_total,
                            documento=f.number,
                        )
                        Invoice.appendChild(prepaid)

        idLine = 1
        for line in self.move_lines:
            if line.product_uom_qty > 0:
                invoiceline = FacturaObject.cacDespatchLine(
                    operacionTipo=self.operacionTipo,
                    idline=idLine,
                    muestra=self.muestra,
                    unitcode=str(line.product_uom.code),#codigos
                    quantity=str(round(line.product_uom_qty, 2)),
                    description=line.name,
                )#
                idLine = idLine + 1
                Invoice.appendChild(invoiceline)


        I = Invoice.toprettyxml("   ")#encoding="utf-8" encoding="ISO-8859-1"
        #I = Invoice.toprettyxml(indent=' ', newl='\r', encoding="utf-8")#indent="\t", encoding="utf-8"
        #I = Invoice.toprettyxml(indent="\t", newl="\n", encoding=None)
        self.documentoXML = I
