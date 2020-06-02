#!/usr/bin/env python
# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.http import request
from odoo.tools.float_utils import float_compare
from utils.InvoiceLine import Factura
from utils.NotaCredito import NotaCredito
from utils.NotaDebito import NotaDebito
from suds.client import Client
from suds.wsse import *
from signxml import XMLSigner, XMLVerifier, methods
from datetime import datetime, timedelta
from cStringIO import StringIO

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


# mapping invoice type to refund type
TYPE2REFUND = {
    "out_invoice": "out_refund",  # Customer Invoice
    "in_invoice": "in_refund",  # Vendor Bill
    "out_refund": "out_invoice",  # Customer Refund
    "in_refund": "in_invoice",  # Vendor Refund
}


class accountInvoice(models.Model):
    _inherit = "account.invoice"

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

    # invoice_type_code = fields.Selection(string="Tipo de Comprobante", store=True, related="journal_id.invoice_type_code_id", readonly=True)
    # invoice_type_code = fields.Char(string="Tipo de Comprobante", default=_set_invoice_type_code, readonly=True)

    # Para documentos de proveedor
    def _list_invoice_type(self):
        catalogs = self.env["einvoice.catalog.01"].search([])
        list = []
        for cat in catalogs:
            list.append((cat.code, cat.name))
        return list

    tipo_documento = fields.Selection(
        string="Tipo de Documento", selection=_list_invoice_type, default="01"
    )
    muestra = fields.Boolean("Muestra", default=False)
    send_route = fields.Selection(
        string="Ruta de envío", store=True, related="company_id.send_route", readonly=True
    )

    response_code = fields.Char("response_code", copy=False)
    referenceID = fields.Char("Referencia", copy=False)
    motivo = fields.Text("Motivo")

    total_venta_gravado = fields.Monetary(
        "Gravado", default=0.0, compute="_compute_total_venta"
    )
    total_venta_inafecto = fields.Monetary(
        "Inafecto", default=0.0, compute="_compute_total_venta"
    )
    total_venta_exonerada = fields.Monetary(
        "Exonerado", default=0.0, compute="_compute_total_venta"
    )
    total_venta_gratuito = fields.Monetary(
        "Gratuita", default=0.0, compute="_compute_total_venta"
    )
    total_descuentos = fields.Monetary(
        "Total Descuentos", default=0.0, compute="_compute_total_venta"
    )

    digestvalue = fields.Char("DigestValue")
    final = fields.Boolean("Es final?", default=False, copy=False)

    # @api.one
    # def _set_invoice_type_code(self):
    #     prueba = self.journal_id.invoice_type_code_id
    #     return prueba

    invoice_type_code = fields.Char(string="Tipo de Comprobante", default="01")

    def set_xml_filename(self):
        self.documentoXMLcliente_fname = str(self.number) + ".xml"

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

    @api.onchange("operacionTipo")
    def validacion_afectacion(self):
        if self.type == "out_invoice":
            if self.invoice_line_ids:
                for line in self.invoice_line_ids:
                    if self.operacionTipo == "0200":
                        line.tipo_afectacion_igv = 16
                    else:
                        line.tipo_afectacion_igv = 1

    @api.onchange("muestra")
    def comment_gratutito(self):
        if self.type == "out_invoice":
            if self.muestra == True:
                self.comment = "Por transferencia a título gratuito de muestras."
                afectacion = 17
            else:
                self.comment = ""
                afectacion = 1

            if self.invoice_line_ids:
                for line in self.invoice_line_ids:
                    line._compute_price()
                    line.tipo_afectacion_igv = afectacion

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
        self, invoice, date_invoice=None, date=None, description=None, journal_id=None
    ):
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
        values["invoice_type_code"] = "07"

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
        res = super(accountInvoice, self).default_get(fields_list)

        journal_id = self.env["account.journal"].search(
            [["invoice_type_code_id", "=", self._context.get("type_code")]], limit=1
        )
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
    def _compute_amount(self):
        if self.muestra == True:
            self.amount_total = 0.00
        else:
            round_curr = self.currency_id.round
            self.amount_untaxed = sum(
                line.price_subtotal for line in self.invoice_line_ids
            )
            self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids)
            self.amount_total = self.amount_untaxed + self.amount_tax
            amount_total_company_signed = self.amount_total
            amount_untaxed_signed = self.amount_untaxed
            if (
                self.currency_id
                and self.company_id
                and self.currency_id != self.company_id.currency_id
            ):
                currency_id = self.currency_id.with_context(date=self.date_invoice)
                amount_total_company_signed = currency_id.compute(
                    self.amount_total, self.company_id.currency_id
                )
                amount_untaxed_signed = currency_id.compute(
                    self.amount_untaxed, self.company_id.currency_id
                )
            sign = self.type in ["in_refund", "out_refund"] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
            self.amount_total_signed = self.amount_total * sign
            self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.one
    @api.depends(
        "invoice_line_ids.price_subtotal",
        "invoice_line_ids.tipo_afectacion_igv",
        "tax_line_ids.amount",
        "currency_id",
        "company_id",
        "date_invoice",
        "type",
    )
    def _compute_total_venta(self):
        # self.total_venta_gravado = sum([line.price_subtotal for line in self.invoice_line_ids if line.tipo_afectacion_igv.code in ('10', '11', '12', '13', '14', '15', '16', '17', '40')])
        # self.total_venta_inafecto = sum([line.price_subtotal for line in self.invoice_line_ids if line.tipo_afectacion_igv.code in ('30', '31', '32', '33', '34', '35', '36')])
        # self.total_venta_exonerada = sum([line.price_subtotal for line in self.invoice_line_ids if line.tipo_afectacion_igv.code == '20'])
        # self.total_venta_gratuito = sum([line.price_subtotal for line in self.invoice_line_ids if line.tipo_afectacion_igv.code in ('21', '37')])
        if self.muestra:
            self.total_venta_gratuito = sum(
                [line.price_subtotal for line in self.invoice_line_ids]
            )
        else:
            self.total_venta_gravado = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if line.tipo_afectacion_igv.code
                    in ("10", "11", "12", "13", "14", "15", "16", "17", "40")
                ]
            )
            self.total_venta_inafecto = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if line.tipo_afectacion_igv.code
                    in ("30", "31", "32", "33", "34", "35", "36")
                ]
            )
            self.total_venta_exonerada = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if line.tipo_afectacion_igv.code == "20"
                ]
            )

        self.total_descuentos = sum(
            [
                line.quantity * line.price_unit * line.discount / 100
                for line in self.invoice_line_ids
            ]
        )

        if self.muestra:
            self.amount_total = 0.0

        self.invoice_type_code = self.journal_id.invoice_type_code_id

    @api.multi
    def firmar(self):
        data_unsigned = ET.fromstring(self.documentoXML.encode("utf-8").strip())

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
        }

        if self.invoice_type_code == "01" or self.invoice_type_code == "03":
            if self.type == "out_invoice":
                namespaces.update(
                    {"": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"}
                )
            elif self.type == "out_refund":
                namespaces.update(
                    {"": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"}
                )
        elif self.invoice_type_code == "07":
            namespaces.update(
                {"": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"}
            )
        elif self.invoice_type_code == "08":
            namespaces.update(
                {"": "urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2"}
            )

        for prefix, uri in namespaces.iteritems():
            ET.register_namespace(prefix, uri)

        uri = "/var/lib/odoo/"

        name_file = (
            self.company_id.partner_id.vat
            + "-"
            + str(self.invoice_type_code)
            + "-"
            + str(self.number)
        )
        file = open(uri + name_file + ".xml", "w")

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

        file.write(ET.tostring(signed_root))

        file.close()

        xfile = open(uri + name_file + ".xml", "r")
        xml_file = xfile.read()
        self.documentoXMLcliente = base64.b64encode(str(xml_file))
        xfile.close()

        zf = zipfile.ZipFile(uri + name_file + ".zip", mode="w")
        try:
            zf.write(uri + name_file + ".xml", arcname=name_file + ".xml")
        except Exception, e:
            zf.close()
        zf.close()

        f = open(uri + name_file + ".zip", "rb")
        data_file = f.read()
        self.documentoZip = base64.b64encode(str(data_file))
        self.documentoXML = ET.tostring(signed_root)

        f.close()

        FacturaObject = Factura()
        EnvioXML = FacturaObject.sendBill(
            username=self.company_id.partner_id.vat + self.company_id.sunat_username,
            password=self.company_id.sunat_password,
            namefile=name_file + ".zip",
            contentfile=self.documentoZip,
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

        try:
            self.documentoRespuestaZip = ET.fromstring(r.text)[0][0][0].text
        except Exception, e:
            self.documentoRespuestaZip = ""

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
                ["journal_id.invoice_type_code_id", "=", "01"],
            ]
        )
        for f in facturas:
            FacturaObject = Factura()
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
        FacturaObject = Factura()
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

            self.firmar()

        response = to_open_invoices.invoice_validate()

        self.numeracion = self.number
        return response

    # line = super(SaleOrderLine, self).create(values)

    @api.multi
    def generarFactura(self):
        ico = self.incoterms_id
        FacturaObject = Factura()
        Invoice = FacturaObject.Root()

        Invoice.appendChild(FacturaObject.UBLExtensions())

        Invoice = FacturaObject.InvoiceRoot(
            rootXML=Invoice,
            versionid="2.1",
            customizationid="2.0",
            id=str(self.number),
            issuedate=str(self.date_invoice),
            issuetime="",
            operacion=self.operacionTipo,
            invoicetypecode=str(self.journal_id.invoice_type_code_id),
            documentcurrencycode=str(self.currency_id.name),
        )

        if self.final:
            facturas = (
                self.env["sale.order"].search([["name", "=", self.origin]]).invoice_ids
            )
            for f in facturas:
                if f.state in ("open", "paid"):
                    if f.number != self.number:
                        additional = FacturaObject.cacAdditionalDocumentReference(
                            documento=f.number,
                            num_doc_ident=str(self.company_id.partner_id.vat),
                            tipo_doc_ident=str(
                                self.company_id.partner_id.catalog_06_id.code
                            ),
                        )
                        Invoice.appendChild(additional)

        Invoice.appendChild(
            FacturaObject.Signature(
                Id="IDSignMT",
                ruc=str(self.company_id.partner_id.vat),
                razon_social=str(self.company_id.partner_id.registration_name),
                uri="#SignatureMT",
            )
        )

        Empresa = FacturaObject.cacAccountingSupplierParty(
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

        Cliente = FacturaObject.cacAccountingCustomerParty(
            num_doc_identidad=num_doc_ident,
            tipo_doc_identidad=doc_code,
            nombre_cliente=nom_cli,
        )

        Invoice.appendChild(Cliente)

        # print('ORIGEN DE FACTURA', self.origin)
        # print('NUMERO DE FACTURA', self.number)
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

        if self.tax_line_ids:
            for tax in self.tax_line_ids:
                TaxTotal = FacturaObject.cacTaxTotal(
                    currency_id=str(self.currency_id.name),
                    taxtotal=str(round(tax.amount, 2)),
                    gratuitas=self.total_venta_gratuito,
                )
                Invoice.appendChild(TaxTotal)
        else:
            TaxTotal = FacturaObject.cacTaxTotal(
                currency_id=str(self.currency_id.name),
                taxtotal="0.0",
                gratuitas=self.total_venta_gratuito,
            )
            Invoice.appendChild(TaxTotal)

        # round_down(n, decimals=0):

        #     return math.floor(n * multiplier) / multiplier

        p1 = 0
        p2 = 0
        # multiplier = 10 ** 2
        round_curr = self.currency_id.round
        for l in self.invoice_line_ids:
            if l.quantity > 0:
                # p1 = p1 + (round_curr(l.price_subtotal)+round_curr(l.price_subtotal*0.18))
                # p1 = p1 + (round_curr(l.price_subtotal+(l.price_subtotal*0.18)))
                p1 = self.amount_total
                # print('P1-1:'+str(round_curr(l.price_subtotal*0.18)))
                # print('P1-2:'+str(l.price_subtotal))
                # print('P1-3:'+str(round_curr(l.price_subtotal)))
                # print('P1-4:'+str(round_curr(l.price_subtotal)+round_curr(l.price_subtotal*0.18)))
            else:
                p2 = p2 + (l.price_subtotal * (-1))

        LegalMonetaryTotal = FacturaObject.cacLegalMonetaryTotal(
            total=p1, prepaid=p2, currency_id=str(self.currency_id.name)
        )
        # LegalMonetaryTotal = FacturaObject.cacLegalMonetaryTotal(
        #     total=round(self.amount_total,2),
        #     prepaid = p2,
        #     currency_id=str(self.currency_id.name)
        # )
        Invoice.appendChild(LegalMonetaryTotal)

        idLine = 1
        for line in self.invoice_line_ids:
            if line.quantity > 0:
                invoiceline = FacturaObject.cacInvoiceLine(
                    operacionTipo=self.operacionTipo,
                    idline=idLine,
                    muestra=self.muestra,
                    valor=str(round(line.price_subtotal, 2)),
                    currency_id=self.currency_id.name,
                    unitcode=str(line.uom_id.code),
                    quantity=str(round(line.quantity, 2)),
                    description=line.name,
                    price=str(round(line.price_unit, 2)),
                    taxtotal=str(
                        round(
                            line.price_subtotal * line.invoice_line_tax_ids.amount / 100,
                            2,
                        )
                    ),
                    afectacion=str(line.tipo_afectacion_igv.code),
                    taxcode=line.invoice_line_tax_ids.tax_group_id.code,
                    taxname=line.invoice_line_tax_ids.tax_group_id.description,
                    taxtype=line.invoice_line_tax_ids.tax_group_id.name_code,
                )
                idLine = idLine + 1
                Invoice.appendChild(invoiceline)

        I = Invoice.toprettyxml("   ")
        self.documentoXML = I

    @api.multi
    def generarNotaCredito(self):
        NotaCreditoObject = NotaCredito()
        nota_credito = NotaCreditoObject.Root()

        nota_credito.appendChild(NotaCreditoObject.UBLExtensions())

        nota_credito = NotaCreditoObject.NotaCreditoRoot(
            rootXML=nota_credito,
            versionid="2.1",
            customizationid="2.0",
            id=str(self.number),
            issue_date=self.date_invoice,
        )

        if self.motivo != False:
            motivo = self.motivo
        else:
            motivo = "Default"

        discrepancy_response = NotaCreditoObject.DiscrepancyResponse(
            reference_id=str(self.origin),
            response_code=str(self.response_code_credito),
            description=motivo,
        )

        document_currency = NotaCreditoObject.documentCurrencyCode(
            documentcurrencycode=str(self.currency_id.name)
        )

        if self.origin[0] == "B":
            DocumentTypeCode = "03"
        elif self.origin[0] == "F":
            DocumentTypeCode = "01"
        else:
            DocumentTypeCode = "-"

        billing_reference = NotaCreditoObject.BillingReference(
            invoice_id=str(self.origin), invoice_type_code=DocumentTypeCode
        )

        signature = NotaCreditoObject.Signature(
            signatureid="IDSignST",
            partyid=str(self.company_id.partner_id.vat),
            partyname=str(self.company_id.partner_id.registration_name),
            uri="#SignatureMT",
        )

        supplierParty = NotaCreditoObject.AccountingSupplierParty(
            registrationname=self.company_id.partner_id.registration_name,
            companyid=str(self.company_id.partner_id.vat),
        )

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

        customerParty = NotaCreditoObject.AccountingCustomerParty(
            customername=nom_cli, customerid=num_doc_ident, customertipo=doc_code
        )

        legal_monetary = NotaCreditoObject.LegalMonetaryTotal(
            payable_amount=str(self.amount_total), currency=self.currency_id.name
        )

        nota_credito.appendChild(document_currency)
        nota_credito.appendChild(discrepancy_response)
        # nota_credito.appendChild(billing_reference)
        nota_credito.appendChild(signature)

        nota_credito.appendChild(supplierParty)
        nota_credito.appendChild(customerParty)

        # if self.tax_line_ids:
        #     for tax in self.tax_line_ids:
        #         TaxTotal=NotaCreditoObject.cacTaxTotal(
        #             currency_id=str(self.currency_id.name),
        #             taxtotal=str(round(tax.amount,2)),
        #             price='0.0',
        #             gratuitas=self.total_venta_gratuito,
        #             gravadas=self.total_venta_gravado,
        #             inafectas=self.total_venta_inafecto,
        #             exoneradas=self.total_venta_exonerada)
        #         nota_credito.appendChild(TaxTotal)

        TaxTotal = NotaCreditoObject.cacTaxTotal(
            currency_id=str(self.currency_id.name),
            taxtotal="0.0",
            price="0.0",
            gratuitas=self.total_venta_gratuito,
            gravadas=self.total_venta_gravado,
            inafectas=self.total_venta_inafecto,
            exoneradas=self.total_venta_exonerada,
        )
        nota_credito.appendChild(TaxTotal)
        nota_credito.appendChild(legal_monetary)

        id = 1
        for line in self.invoice_line_ids:
            a = NotaCreditoObject.CreditNoteLine(
                id=str(id),
                valor=str(round(line.price_subtotal, 2)),
                unitCode=str(line.uom_id.code),
                quantity=str(round(line.quantity, 2)),
                currency=self.currency_id.name,
                price=str(round(line.price_unit, 2)),
                taxtotal=str(
                    round(line.price_subtotal * line.invoice_line_tax_ids.amount / 100, 2)
                ),
                afectacion=str(line.tipo_afectacion_igv.code),
            )
            id = id + 1
            nota_credito.appendChild(a)

        I = nota_credito.toprettyxml("   ")
        self.documentoXML = I

    @api.multi
    def generarNotaDebito(self):
        NotaDebitoObject = NotaDebito()
        nota_debito = NotaDebitoObject.Root()

        nota_debito.appendChild(NotaDebitoObject.UBLExtensions())

        nota_debito = NotaDebitoObject.NotaDebitoRoot(
            rootXML=nota_debito,
            versionid="2.1",
            customizationid="2.0",
            id=str(self.number),
            issue_date=self.date_invoice,
            documentcurrencycode=str(self.currency_id.name),
        )

        if self.motivo != False:
            motivo = self.motivo
        else:
            motivo = "Default"

        discrepancy_response = NotaDebitoObject.DiscrepancyResponse(
            reference_id=str(self.origin),
            response_code=str(self.response_code_debito),
            description=motivo,
        )
        # discrepancy_response = NotaDebitoObject.DiscrepancyResponse(
        #                             reference_id = str(self.referenceID),
        #                             response_code = str(self.response_code_debito),
        #                             description = motivo)

        if self.referenceID[0] == "B":
            DocumentTypeCode = "03"
        elif self.referenceID[0] == "F":
            DocumentTypeCode = "01"
        else:
            DocumentTypeCode = "-"

        billing_reference = NotaDebitoObject.BillingReference(
            invoice_id=str(self.referenceID), invoice_type_code=DocumentTypeCode
        )

        signature = NotaDebitoObject.Signature(
            signatureid="IDSignST",
            partyid=str(self.company_id.partner_id.vat),
            partyname=str(self.company_id.partner_id.registration_name),
            uri="#SignatureMT",
        )

        supplierParty = NotaDebitoObject.AccountingSupplierParty(
            registrationname=self.company_id.partner_id.registration_name,
            companyid=str(self.company_id.partner_id.vat),
        )

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

        customerParty = NotaDebitoObject.AccountingCustomerParty(
            customername=nom_cli, customerid=num_doc_ident, customertipo=doc_code
        )

        request_monetary = NotaDebitoObject.RequestedMonetaryTotal(
            payable_amount=str(self.amount_total)
        )

        nota_debito.appendChild(discrepancy_response)
        nota_debito.appendChild(billing_reference)
        nota_debito.appendChild(signature)
        nota_debito.appendChild(supplierParty)
        nota_debito.appendChild(customerParty)

        impuestos = 0.00
        for tax in self.tax_line_ids:
            impuestos += tax.amount

        TaxTotal = NotaDebitoObject.cacTaxTotal(
            currency_id=str(self.currency_id.name),
            taxtotal=str(round(impuestos, 2)),
            gravado=str(round(self.total_venta_gravado)),
            inafecto=str(round(self.total_venta_inafecto)),
            exonerado=str(round(self.total_venta_exonerada)),
            gratuito=str(round(self.total_venta_gratuito)),
        )

        nota_debito.appendChild(TaxTotal)
        nota_debito.appendChild(request_monetary)

        id = 1
        for line in self.invoice_line_ids:
            a = NotaDebitoObject.DebitNoteLine(
                id=str(id),
                valor=str(round(line.price_subtotal, 2)),
                unitCode=str(line.uom_id.code),
                quantity=str(round(line.quantity, 2)),
                currency=self.currency_id.name,
                price=str(round(line.price_unit, 2)),
                taxtotal=str(
                    round(line.price_subtotal * line.invoice_line_tax_ids.amount / 100, 2)
                ),
                afectacion=str(line.tipo_afectacion_igv.code),
            )
            id = id + 1
            nota_debito.appendChild(a)

        I = nota_debito.toprettyxml("   ")
        self.documentoXML = I


# REGISTRO DE COMPRAS
class PrintReportTextCompras(models.TransientModel):
    _name = "print.compras.reporte.contabilidad"

    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list

    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Reporte de Compras")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Reporte de Compras")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )

    @api.multi
    def generaReporte(self):
        monthRange = calendar.monthrange(int(self.years), int(self.months))

        invoice_objs = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.years + "-" + self.months + "-01"),
                (
                    "date_invoice",
                    "<=",
                    self.years + "-" + self.months + "-" + str(monthRange[1]),
                ),
                ("type", "=", "in_invoice"),
                ("state", "not in", ["draft", "cancel"]),
            ]
        )

        for wizard in self:
            fp = StringIO()
            cuo = 1
            for line in invoice_objs:
                di = datetime.strptime(line.date_invoice, "%Y-%m-%d")
                di = unicode(di.date()).split("-")
                fdi = "/".join(reversed(di))

                if line.date_due is False:
                    dd = line.date_invoice
                else:
                    dd = line.date_due
                # Por mientras
                dd = ""

                if line.partner_id.parent_id:
                    doccode = line.partner_id.parent_id.catalog_06_id.code
                    vatcode = line.partner_id.parent_id.vat
                    docname = line.partner_id.parent_id.name
                else:
                    doccode = line.partner_id.catalog_06_id.code
                    vatcode = line.partner_id.vat
                    docname = line.partner_id.name
                ac = "M" + unicode(cuo).zfill(3)

                if line.reference is False:
                    reference = "0-0"
                else:
                    reference = line.reference

                compras = (
                    self.years
                    + self.months
                    + "00"
                    + "|"
                    + unicode(cuo)
                    + "|"
                    + unicode(ac)
                    + "|"
                    + unicode(fdi)
                    + "|"
                    + unicode(dd)
                    + "|"
                    + unicode(line.tipo_documento)
                    + "|"
                    + unicode(reference.split("-")[0])
                    + "|"
                    + ""
                    + "|"
                    + unicode(reference.split("-")[1])
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.partner_id.catalog_06_id.code)
                    + "|"
                    + unicode(line.partner_id.vat)
                    + "|"
                    + unicode(line.partner_id.name)
                    + "|"
                    + unicode(line.amount_untaxed)
                    + "|"
                    + unicode(line.amount_tax)
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.amount_total)
                    + "|"
                    + unicode(line.currency_id.name)
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + "1"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + "1"
                    + "\n"
                )

                fp.write(compras.encode("utf-8"))
                cuo = cuo + 1

            file_text_name = (
                "LE"
                + self.create_uid.company_id.vat
                + self.years
                + self.months
                + "0008010000"
                + "1111.txt"
            )

            excel_file = base64.encodestring(fp.getvalue())
            wizard.invoice_summary_file = excel_file
            # wizard.file_name = "Compras.txt"
            wizard.file_name = file_text_name
            wizard.invoice_report_printed = True
            fp.close()

            return {
                "view_mode": "form",
                "res_id": wizard.id,
                "res_model": "print.compras.reporte.contabilidad",
                "view_type": "form",
                "type": "ir.actions.act_window",
                "context": wizard.env.context,
                "target": "new",
            }


# REGISTRO DE VENTAS
class PrintReportTextVentas(models.TransientModel):
    _name = "print.ventas.reporte.contabilidad"

    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list

    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Reporte de Ventas")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Reporte de Ventas")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )

    @api.multi
    def generaReporte(self):
        monthRange = calendar.monthrange(int(self.years), int(self.months))

        invoice_objs = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.years + "-" + self.months + "-01"),
                (
                    "date_invoice",
                    "<=",
                    self.years + "-" + self.months + "-" + str(monthRange[1]),
                ),
                ("type", "=", "out_invoice"),
                ("state", "not in", ["draft", "cancel"]),
            ]
        )

        for wizard in self:
            fp = StringIO()
            cuo = 1
            for line in invoice_objs:
                di = datetime.strptime(line.date_invoice, "%Y-%m-%d")
                di = unicode(di.date()).split("-")
                fdi = "/".join(reversed(di))

                if line.date_due is False:
                    dd = line.date_invoice
                else:
                    dd = line.date_due
                # Por mientras
                dd = ""

                if line.partner_id.parent_id:
                    doccode = line.partner_id.parent_id.catalog_06_id.code
                    vatcode = line.partner_id.parent_id.vat
                    docname = line.partner_id.parent_id.name
                else:
                    doccode = line.partner_id.catalog_06_id.code
                    vatcode = line.partner_id.vat
                    docname = line.partner_id.name
                ac = "M" + unicode(cuo).zfill(3)

                ventas = (
                    self.years
                    + self.months
                    + "00"
                    + "|"
                    + unicode(cuo)
                    + "|"
                    + unicode(ac)
                    + "|"
                    + unicode(fdi)
                    + "|"
                    + unicode(dd)
                    + "|"
                    + unicode(line.tipo_documento)
                    + "|"
                    + unicode(line.number.split("-")[0])
                    + "|"
                    + unicode(line.number.split("-")[1])
                    + "|"
                    + ""
                    + "|"
                    + unicode(doccode)
                    + "|"
                    + unicode(vatcode)
                    + "|"
                    + unicode(docname)
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.amount_untaxed)
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.amount_tax)
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.amount_total)
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + "1"
                    + "|"
                    + "1"
                    + "|"
                    + ""
                    + "\n"
                )

                fp.write(ventas.encode("utf-8"))
                cuo = cuo + 1

            file_text_name = (
                "LE"
                + self.create_uid.company_id.vat
                + self.years
                + self.months
                + "0014010000"
                + "1111.txt"
            )
            excel_file = base64.encodestring(fp.getvalue())
            wizard.invoice_summary_file = excel_file
            # wizard.file_name = "Ventas.txt"
            wizard.file_name = file_text_name
            wizard.invoice_report_printed = True
            fp.close()

            return {
                "view_mode": "form",
                "res_id": wizard.id,
                "res_model": "print.ventas.reporte.contabilidad",
                "view_type": "form",
                "type": "ir.actions.act_window",
                "context": wizard.env.context,
                "target": "new",
            }


# REGISTRO DIARIO
class PrintReportTextDiario(models.TransientModel):
    _name = "print.diario.reporte.contabilidad"

    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list

    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Reporte de Diario")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Reporte de Diario")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )

    @api.multi
    def generaReporte(self):
        monthRange = calendar.monthrange(int(self.years), int(self.months))

        invoice_objs = self.env["account.move.line"].search(
            [
                ("date", ">=", self.years + "-" + self.months + "-01"),
                ("date", "<=", self.years + "-" + self.months + "-" + str(monthRange[1])),
            ]
        )

        for wizard in self:
            fp = StringIO()
            cuo = 1
            for line in invoice_objs:
                di = datetime.strptime(line.date, "%Y-%m-%d")
                di = unicode(di.date()).split("-")
                fdi = "/".join(reversed(di))

                if line.date_maturity is False:
                    dd = line.date
                else:
                    dd = line.date_maturity

                if line.move_id.name.find("-") > 0:
                    documento = self.env["account.invoice"].search(
                        [("number", "=", line.move_id.name)]
                    )

                    tipo = documento.tipo_documento
                    serie = documento.number.split("-")[0]
                    numero = documento.number.split("-")[1]
                else:
                    tipo = ""
                    serie = ""
                    numero = ""

                ac = "M" + unicode(cuo).zfill(3)
                diario = (
                    self.years
                    + self.months
                    + "00"
                    + "|"
                    + unicode(cuo)
                    + "|"
                    + unicode(ac)
                    + "|"
                    + unicode(line.account_id.code)
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.move_id.name)
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + unicode(tipo)
                    + "|"
                    + unicode(serie)
                    + "|"
                    + unicode(numero)
                    + "|"
                    + unicode(fdi)
                    + "|"
                    + unicode(dd).replace("-", "/")
                    + "|"
                    + unicode(fdi)
                    + "|"
                    + unicode(line.name)
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.debit)
                    + "|"
                    + unicode(line.credit)
                    + "|"
                    + ""
                    + "|"
                    + "1"
                    + "|"
                    + ""
                    + "\n"
                )

                fp.write(diario.encode("utf-8"))
                cuo = cuo + 1

            # LERRRRRRRRRRRAAAAMM0005020000OIM1.TXT
            file_text_name = (
                "LE"
                + self.create_uid.company_id.vat
                + self.years
                + self.months
                + "0005020000"
                + "1111.txt"
            )
            excel_file = base64.encodestring(fp.getvalue())
            wizard.invoice_summary_file = excel_file
            # wizard.file_name = "Diario_ventas.txt"
            wizard.file_name = file_text_name
            wizard.invoice_report_printed = True
            fp.close()

            return {
                "view_mode": "form",
                "res_id": wizard.id,
                "res_model": "print.diario.reporte.contabilidad",
                "view_type": "form",
                "type": "ir.actions.act_window",
                "context": wizard.env.context,
                "target": "new",
            }


# PLAN CONTABLE
class PrintReportPlanContable(models.TransientModel):
    _name = "print.plancontable.reporte.contabilidad"

    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list

    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Plan Contable")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Plan contable")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )

    @api.multi
    def generaReporte(self):
        plan_object = self.env["account.account"].search([])

        for wizard in self:
            fp = StringIO()

            for line in plan_object:
                plan = (
                    self.years
                    + self.months
                    + "00"
                    + "|"
                    + unicode(line.code)
                    + "|"
                    + unicode(line.name)
                    + "|"
                    + "01"
                    + "|"
                    + "-"
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + "1"
                    + "\n"
                )

                fp.write(plan.encode("utf-8"))

            # LERRRRRRRRRRRAAAAMM0005040000OIM1.TXT
            file_text_name = (
                "LE"
                + self.create_uid.company_id.vat
                + self.years
                + self.months
                + "0005040000"
                + "1111.txt"
            )
            excel_file = base64.encodestring(fp.getvalue())
            wizard.invoice_summary_file = excel_file
            # wizard.file_name = "Plan_contable.txt"
            wizard.file_name = file_text_name
            wizard.invoice_report_printed = True
            fp.close()

            return {
                "view_mode": "form",
                "res_id": wizard.id,
                "res_model": "print.plancontable.reporte.contabilidad",
                "view_type": "form",
                "type": "ir.actions.act_window",
                "context": wizard.env.context,
                "target": "new",
            }
