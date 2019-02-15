#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from utils.InvoiceLine import Factura
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

class invoice_factura(models.Model):
    _inherit = "account.invoice"
    @api.multi
    def generarFactura(self):
        ico = self.incoterms_id
        FacturaObject = Factura()
        Invoice = FacturaObject.Root()

        Invoice.appendChild(FacturaObject.UBLExtensions())

        Invoice = FacturaObject.InvoiceRoot(
			rootXML = Invoice,
            versionid = "2.1",
            customizationid = "2.0",
            id = str(self.number),
            issuedate = str(self.date_invoice),
            issuetime = "",
            operacion=self.operacionTipo,
            invoicetypecode = str(self.journal_id.invoice_type_code_id),
            documentcurrencycode = str(self.currency_id.name))

        Invoice.appendChild(FacturaObject.Signature(
			Id="IDSignMT",
			ruc=str(self.company_id.partner_id.vat),
			razon_social=str(self.company_id.partner_id.registration_name),
			uri="#SignatureMT"))

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
			codigo_pais="PE")

        Invoice.appendChild(Empresa)

        # DOCUMENTO DE IDENTIDAD
        num_doc_ident = str(self.partner_id.vat)
        if num_doc_ident == 'False':
            num_doc_ident = '-'
        
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
			nombre_cliente=nom_cli)

        Invoice.appendChild(Cliente)

        if self.tax_line_ids:
            for tax in self.tax_line_ids:
                # TaxTotal=FacturaObject.cacTaxTotal(
                #     currency_id=str(self.currency_id.name),
                #     taxtotal=str(round(tax.amount,2)),
                #     gravadas=str(round(self.total_venta_gravado,2)),
                #     igv=str(round(tax.amount,2)),
                #     tributo_code=str(tax.tax_id.tax_group_id.name_code),
                #     tributo_name=str(tax.tax_id.tax_group_id.description),
                #     tributo_id=str(tax.tax_id.tax_group_id.code))
                TaxTotal=FacturaObject.cacTaxTotal(
                    currency_id=str(self.currency_id.name),
                    taxtotal=str(round(tax.amount,2)),
                    gratuitas=self.total_venta_gratuito)
                Invoice.appendChild(TaxTotal)
        else:
            TaxTotal=FacturaObject.cacTaxTotal(
                currency_id=str(self.currency_id.name),
                taxtotal='0.0',
                gratuitas=self.total_venta_gratuito)
            Invoice.appendChild(TaxTotal)

        LegalMonetaryTotal = FacturaObject.cacLegalMonetaryTotal(
            total=round(self.amount_total,2),
            currency_id=str(self.currency_id.name)
        )
        Invoice.appendChild(LegalMonetaryTotal)

        idLine = 1
        for line in self.invoice_line_ids:
            invoiceline = FacturaObject.cacInvoiceLine(
                            operacionTipo=self.operacionTipo,
                            idline=idLine,
                            valor=str(round(line.price_subtotal, 2)),
                            currency_id=self.currency_id.name,
                            unitcode=str(line.uom_id.code),
                            quantity=str(round(line.quantity, 2)),
                            description=line.name,
                            price=str(round(line.price_unit, 2)),
                            taxtotal=str(round(line.price_subtotal*line.invoice_line_tax_ids.amount/100,2)),
                            afectacion=str(line.tipo_afectacion_igv.code),
                            taxcode=line.invoice_line_tax_ids.tax_group_id.code,
                            taxname=line.invoice_line_tax_ids.tax_group_id.description,
                            taxtype=line.invoice_line_tax_ids.tax_group_id.name_code)

            idLine = idLine+1
            Invoice.appendChild(invoiceline)

        I=Invoice.toprettyxml("   ")
        self.documentoXML =  I