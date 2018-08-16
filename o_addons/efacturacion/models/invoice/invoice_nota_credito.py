#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from utils.InvoiceLine import Factura
from utils.Boleta import Boleta
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


class invoice_nota_credito(models.Model):
    _inherit = "account.invoice"
    @api.multi
    def generarNotaCredito(self):
        NotaCreditoObject=NotaCredito()
        nota_credito=NotaCreditoObject.Root()

        Total = NotaCreditoObject.AdditionalMonetaryTotal(gravado=str(round(self.total_venta_gravado, 2)),
                                                          exonerado=str(round(self.total_venta_exonerada, 2)),
                                                          inafecto=str(round(self.total_venta_inafecto, 2)),
                                                          gratuito=str(round(self.total_venta_gratuito, 2)),
                                                          total_descuento=str(round(self.total_descuentos, 2)),
                                                          currencyID=str(self.company_id.currency_id.name))
        firma = NotaCreditoObject.firma("placeholder")
        Total.appendChild(firma)

        nota_credito.appendChild(Total)

        nota_credito=NotaCreditoObject.NotaCreditoRoot(root=nota_credito,ubl_version_id="2.0", customization_id="1.0",
                                                       summary_id=str(self.number),
                                                       issue_date=self.date_invoice,
                                                       issue_time=False,
                                                       currency_code=str(self.company_id.currency_id.name))

        if self.motivo != False:
            motivo = self.motivo
        else:
            motivo = "Default"

        discrepancy_response = NotaCreditoObject.DiscrepancyResponse(reference_id=str(self.referenceID),
                                                                     response_code=str(self.response_code_credito),
                                                                     description=motivo)
                                                                     #description=str(self.motivo if self.motivo!=False else "" ))

        DocumentTypeCode="03" if self.referenceID[0]=="B" else ("01" if self.referenceID[0]=="F" else "-")

        billing_reference = NotaCreditoObject.BillingReference(invoice_id=str(self.referenceID),
                                                               invoice_type_code=DocumentTypeCode)

        signature = NotaCreditoObject.Signature(signature_id="IDSignSt",
                                                party_id=str(self.company_id.partner_id.vat),
                                                party_name=str(self.company_id.partner_id.registration_name),
                                                uri="#SignatureSP")

        supplier_party = NotaCreditoObject.cacAccountingSupplierParty(num_doc_ident=str(self.company_id.partner_id.vat),
                                                           tipo_doc_ident=str(
                                                               self.company_id.partner_id.catalog_06_id.code),
                                                           nombre_comercial=self.company_id.partner_id.registration_name,
                                                           codigo_ubigeo=str(self.company_id.partner_id.zip),
                                                           nombre_direccion_full=str(self.company_id.partner_id.street),
                                                           nombre_direccion_division=
                                                               self.company_id.partner_id.street2,
                                                           nombre_departamento=str(
                                                               self.company_id.partner_id.state_id.name),
                                                           nombre_provincia=str(
                                                               self.company_id.partner_id.province_id.name),
                                                           nombre_distrito=str(
                                                               self.company_id.partner_id.district_id.name),
                                                           nombre_proveedor=str(
                                                               self.company_id.partner_id.registration_name),
                                                           codigo_pais="PE")
############################################
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
###############################################        
        
        customer_party = NotaCreditoObject.cacAccountCustomerParty(num_doc_identidad=num_doc_ident,
                                                        tipo_doc_identidad=doc_code,
                                                        nombre_cliente=nom_cli)
        # customer_party = NotaCreditoObject.cacAccountCustomerParty(num_doc_identidad=str(self.partner_id.vat),
        #                                                 tipo_doc_identidad=str(self.partner_id.catalog_06_id.code),
        #                                                 nombre_cliente=str(self.partner_id.registration_name))

        nota_credito.appendChild(discrepancy_response)
        nota_credito.appendChild(billing_reference)
        nota_credito.appendChild(signature)
        nota_credito.appendChild(supplier_party)
        nota_credito.appendChild(customer_party)

        for tax in self.tax_line_ids:
            TaxTotal=NotaCreditoObject.TaxTotal(currencyID=str(self.company_id.currency_id.name),
                                                       TaxAmount=str(round(tax.amount,2)),
                                                       tributo_codigo=str(tax.tax_id.tax_group_id.name_code),
                                                       tributo_nombre=str(tax.tax_id.tax_group_id.description),
                                                       tributo_id=str(tax.tax_id.tax_group_id.code))
            nota_credito.appendChild(TaxTotal)

        legal_monetary = NotaCreditoObject.LegalMonetaryTotal(payable_amount=str(self.amount_total))

        nota_credito.appendChild(legal_monetary)

        id = 1
        for line in self.invoice_line_ids:

            TaxTotals = []

            # Si No hay impuestos puede tratarse de un tipo de igv inafecto o exonerado
            if len(line.invoice_line_tax_ids) == 0:
                taxDict = {
                    "currencyID": str(self.company_id.currency_id.name),
                    "TaxAmount": str(0.00),
                    "TaxExemptionReasonCode": str(line.tipo_afectacion_igv.code),
                    "tributo_codigo": "1000", "tributo_nombre": "IGV",
                    "tributo_tipo_codigo": "VAT", "TierRange": "01"
                }
                TaxTotal = NotaCreditoObject.cacTaxTotal(taxDict)
                TaxTotals.append(TaxTotal)

            subtotal = line.price_subtotal
            for tax in line.invoice_line_tax_ids.sorted(key=lambda r: r.tax_group_id.sequence):

                if tax.price_include == True:
                    if tax.amount_type == "percent":
                        taxDict = {
                            "currencyID": self.company_id.currency_id.name,
                            "TaxAmount": str(round(subtotal * tax.amount / 100, 2)),
                            "TaxExemptionReasonCode": str(line.tipo_afectacion_igv.code),
                            "tributo_codigo": tax.tax_group_id.code,
                            "tributo_nombre": tax.tax_group_id.description,
                            "tributo_tipo_codigo": tax.tax_group_id.name_code,
                            "TierRange": "01"
                        }

                        TaxTotal = NotaCreditoObject.cacTaxTotal(taxDict)
                        TaxTotals.append(TaxTotal)
                        subtotal = subtotal * (1 + tax.amount / 100)


            a = NotaCreditoObject.CreditNoteLine(amount=str(round(line.price_subtotal, 2)),
                                          currencyID=self.company_id.currency_id.name,
                                          ID=str(id),
                                          precio_unitario=round(line.price_unit, 2),
                                          quantity=str(round(line.quantity, 2)),
                                          unitCode=str(line.uom_id.code.encode('utf-8')),
                                          no_onerosa=line.tipo_afectacion_igv.no_onerosa,
                                          valor_unitario=str(line.product_id.lst_price))


            for Tax in TaxTotals:
                a.appendChild(Tax)

            # discount = (line.price_subtotal if line.price_subtotal else 0.0) * (line.discount / 100)
            # a.appendChild(NotaCreditoObject.cacItem(str(line.product_id.id), line.name))
            # a.appendChild(NotaCreditoObject.cacPrice(str(line.price_subtotal)))
            # discount = (line.price_unit if line.price_unit else 0.0) * (line.discount / 100)
            a.appendChild(NotaCreditoObject.cacItem(str(line.product_id.id), line.name))
            a.appendChild(NotaCreditoObject.cacPrice(str(line.price_unit)))
            # if discount > 0:
                # a.appendChild(
                    # NotaCreditoObject.AllowanceCharge(str(round(discount, 2)), str(self.company_id.currency_id.name)))
            id = id + 1
            nota_credito.appendChild(a)

        # I = nota_credito.toprettyxml("        ")
        # self.documentoXML='<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?>'+I

        I=nota_credito.toprettyxml("   ")
        self.documentoXML =  I
