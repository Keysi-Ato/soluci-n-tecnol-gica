#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from utils.InvoiceLine import Factura
from utils.NotaCredito import NotaCredito
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


class invoice_nota_credito(models.Model):
    _inherit = "account.invoice"
    @api.multi
    def generarNotaCredito(self):
        NotaCreditoObject = NotaCredito()
        nota_credito = NotaCreditoObject.Root()
        
        nota_credito.appendChild(NotaCreditoObject.UBLExtensions())

        nota_credito = NotaCreditoObject.NotaCreditoRoot(
                        rootXML = nota_credito,
                        versionid = "2.1",
                        customizationid = "2.0",
                        id = str(self.number),
                        issue_date = self.date_invoice,
                        documentcurrencycode = str(self.company_id.currency_id.name))

        if self.motivo != False:
            motivo = self.motivo
        else:
            motivo = "Default"

        discrepancy_response = NotaCreditoObject.DiscrepancyResponse(
                                    reference_id = str(self.referenceID),
                                    response_code = str(self.response_code_credito),
                                    description = motivo)

        if self.referenceID[0] == "B":
            DocumentTypeCode = "03"
        elif self.referenceID[0] == "F":
            DocumentTypeCode = "01"
        else:
            DocumentTypeCode = "-"
        
        billing_reference = NotaCreditoObject.BillingReference(
                                invoice_id=str(self.referenceID),
                                invoice_type_code=DocumentTypeCode)


        signature = NotaCreditoObject.Signature(
                        signatureid="IDSignST",
                        partyid=str(self.company_id.partner_id.vat),
                        partyname=str(self.company_id.partner_id.registration_name),
                        uri="#SignatureSP")

        supplierParty = NotaCreditoObject.AccountingSupplierParty(
                            registrationname = self.company_id.partner_id.registration_name,
                            companyid = str(self.company_id.partner_id.vat))


        # DOCUMENTO DE IDENTIDAD
        num_doc_ident = str(self.partner_id.vat)
        if num_doc_ident == 'False':
            num_doc_ident = '-'
        
        parent = self.partner_id.parent_id
        if parent:
            # doc_code = str(self.partner_id.parent_id.catalog_06_id.code)
            nom_cli = self.partner_id.parent_id.registration_name
            if nom_cli == False:
                nom_cli = self.partner_id.parent_id.name
        else:
            # doc_code = str(self.partner_id.catalog_06_id.code)
            nom_cli = self.partner_id.registration_name
            if nom_cli == False:
                nom_cli = self.partner_id.name
        
        customerParty = NotaCreditoObject.AccountingCustomerParty(
                            customername = nom_cli,
                            customerid = num_doc_ident)
        
        legal_monetary = NotaCreditoObject.LegalMonetaryTotal(payable_amount=str(self.amount_total))

        nota_credito.appendChild(discrepancy_response)
        # nota_credito.appendChild(billing_reference)
        nota_credito.appendChild(signature)
        
        nota_credito.appendChild(supplierParty)
        nota_credito.appendChild(customerParty)
        

        if self.tax_line_ids:
            for tax in self.tax_line_ids:
                TaxTotal=NotaCreditoObject.cacTaxTotal(
                    currency_id=str(self.currency_id.name),
                    taxtotal=str(round(tax.amount,2)),
                    price='0.0',
                    gratuitas=self.total_venta_gratuito,
                    gravadas=self.total_venta_gravado,
                    inafectas=self.total_venta_inafecto,
                    exoneradas=self.total_venta_exonerada)
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
                    taxtotal=str(round(line.price_subtotal*line.invoice_line_tax_ids.amount/100, 2)),
                    afectacion=str(line.tipo_afectacion_igv.code))
            id = id + 1
            nota_credito.appendChild(a)

        I=nota_credito.toprettyxml("   ")
        self.documentoXML =  I