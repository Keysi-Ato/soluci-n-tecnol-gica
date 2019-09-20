#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from utils.InvoiceLine import Factura
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


class invoice_nota_debito(models.Model):
    _inherit = "account.invoice"
    @api.multi
    def generarNotaDebito(self):
        NotaDebitoObject = NotaDebito()
        nota_debito = NotaDebitoObject.Root()
        
        nota_debito.appendChild(NotaDebitoObject.UBLExtensions())

        nota_debito = NotaDebitoObject.NotaDebitoRoot(
                        rootXML = nota_debito,
                        versionid = "2.1",
                        customizationid = "2.0",
                        id = str(self.number),
                        issue_date = self.date_invoice,
                        documentcurrencycode = str(self.company_id.currency_id.name))

        if self.motivo != False:
            motivo = self.motivo
        else:
            motivo = "Default"

        discrepancy_response = NotaDebitoObject.DiscrepancyResponse(
                                    reference_id = str(self.referenceID),
                                    response_code = str(self.response_code_debito),
                                    description = motivo)

        if self.referenceID[0] == "B":
            DocumentTypeCode = "03"
        elif self.referenceID[0] == "F":
            DocumentTypeCode = "01"
        else:
            DocumentTypeCode = "-"
        
        billing_reference = NotaDebitoObject.BillingReference(
                                invoice_id=str(self.referenceID),
                                invoice_type_code=DocumentTypeCode)

        signature = NotaDebitoObject.Signature(
                        signatureid="IDSignST",
                        partyid=str(self.company_id.partner_id.vat),
                        partyname=str(self.company_id.partner_id.registration_name),
                        uri="#SignatureSP")

        supplierParty = NotaDebitoObject.AccountingSupplierParty(
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
        
        customerParty = NotaDebitoObject.AccountingCustomerParty(
                            customername = nom_cli,
                            customerid = num_doc_ident)
        
        request_monetary = NotaDebitoObject.RequestedMonetaryTotal(payable_amount=str(self.amount_total))

        nota_debito.appendChild(discrepancy_response)
        nota_debito.appendChild(billing_reference)
        nota_debito.appendChild(signature)
        nota_debito.appendChild(supplierParty)
        nota_debito.appendChild(customerParty)
        
    
        # if self.tax_line_ids:
        #     for tax in self.tax_line_ids:
        #         TaxTotal = NotaDebitoObject.cacTaxTotal(
        #             currency_id = str(self.currency_id.name),
        #             taxtotal = str(round(tax.amount,2)))
        #         nota_debito.appendChild(TaxTotal)
        # else:
        #     TaxTotal = NotaDebitoObject.cacTaxTotal(
        #         currency_id = str(self.currency_id.name),
        #         taxtotal = '0.0')
        #     nota_debito.appendChild(TaxTotal)

        impuestos = 0.00
        for tax in self.tax_line_ids:
            impuestos += tax.amount
                
        TaxTotal = NotaDebitoObject.cacTaxTotal(
            currency_id = str(self.currency_id.name),
            taxtotal = str(round(impuestos, 2)),
            gravado = str(round(self.total_venta_gravado)),
            inafecto = str(round(self.total_venta_inafecto)),
            exonerado = str(round(self.total_venta_exonerada)),
            gratuito = str(round(self.total_venta_gratuito)),
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
                    taxtotal=str(round(line.price_subtotal*line.invoice_line_tax_ids.amount/100, 2)),
                    afectacion=str(line.tipo_afectacion_igv.code))
            id = id + 1
            nota_debito.appendChild(a)

        I=nota_debito.toprettyxml("   ")
        self.documentoXML =  I