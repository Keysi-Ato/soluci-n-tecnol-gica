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


class invoice_nota_debito(models.Model):
    _inherit = "account.invoice"
    @api.multi
    def generarNotaDebito(self):
        NotaDebitoObject = NotaDebito()
        nota_debito =NotaDebitoObject.Root()
        Total = NotaDebitoObject.AdditionalMonetaryTotal(gravado=str(round(self.total_venta_gravado, 2)),
                                                      exonerado=str(round(self.total_venta_exonerada, 2)),
                                                      inafecto=str(round(self.total_venta_inafecto, 2)),
                                                      gratuito=str(round(self.total_venta_gratuito, 2)),
                                                      total_descuento=str(round(self.total_descuentos, 2)),
                                                      currencyID=str(self.company_id.currency_id.name))
        Total.appendChild(NotaDebitoObject.firma(id="placeholder"))
        nota_debito.appendChild(Total)


        nota_debito = NotaDebitoObject.NotaDebitoRoot(root=nota_debito,ubl_version_id="2.0",
                                                      customization_id="1.0",
                                                      summary_id=str(self.number),
                                                      issue_date=self.date_invoice,
                                                      currency_code=self.company_id.currency_id.name)


        discrepancy_response = NotaDebitoObject.DiscrepancyResponse(reference_id=self.referenceID, response_code="01",
                                                                    description="Aplicacion de intereses")
        nota_debito.appendChild(discrepancy_response)

        billing_reference = NotaDebitoObject.BillingReference(invoice_id=str(self.origin), invoice_type_code="01")

        nota_debito.appendChild(billing_reference)

        signature = NotaDebitoObject.Signature(signature_id="IDSignSP", party_id=str(self.company_id.partner_id.vat),
                                               party_name=str(self.company_id.partner_id.registration_name), uri="#SignatureSP")
        nota_debito.appendChild(signature)


        supplier_party =NotaDebitoObject.cacAccountingSupplierParty(num_doc_ident=str(self.company_id.partner_id.vat),
                                                         tipo_doc_ident=str(self.company_id.partner_id.catalog_06_id.code),
                                                         nombre_comercial=self.company_id.partner_id.registration_name,
                                                         codigo_ubigeo=str(self.company_id.partner_id.zip),
                                                         nombre_direccion_full=str(self.company_id.partner_id.street),
                                                         nombre_direccion_division=str(self.company_id.partner_id.street2 if self.company_id.partner_id.street2 else ""),
                                                         nombre_departamento=str(self.company_id.partner_id.state_id.name),
                                                         nombre_provincia=str(self.company_id.partner_id.province_id.name),
                                                         nombre_distrito=str(self.company_id.partner_id.district_id.name),
                                                         nombre_proveedor=str(self.company_id.partner_id.registration_name),
                                                         codigo_pais="PE")
        nota_debito.appendChild(supplier_party)
        customer_party = NotaDebitoObject.cacAccountCustomerParty(num_doc_identidad=str(self.partner_id.vat),
                                                      tipo_doc_identidad=str(self.partner_id.catalog_06_id.code),
                                                      nombre_cliente=str(self.partner_id.registration_name))
        nota_debito.appendChild(customer_party)

        for tax in self.tax_line_ids:
            TaxTotal=NotaDebitoObject.TaxTotal(currencyID=str(self.company_id.currency_id.name),
                                                       TaxAmount=str(round(tax.amount,2)),
                                                       tributo_codigo=str(tax.tax_id.tax_group_id.name_code),
                                                       tributo_nombre=str(tax.tax_id.tax_group_id.description),
                                                       tributo_id=str(tax.tax_id.tax_group_id.code))
            nota_debito.appendChild(TaxTotal)

        legal_monetary = NotaDebitoObject.RequestedMonetaryTotal(payable_amount=str(self.amount_total))
        nota_debito.appendChild(legal_monetary)

        line_id = 1
        for line in self.invoice_line_ids:
            TaxTotals = []
            subtotal = line.price_subtotal
            subtotal_tax = 0
            tax_count = 0
            for tax in line.invoice_line_tax_ids.sorted(key=lambda r: r.tax_group_id.sequence):
                taxDict = {
                    "TaxAmount": str(round(subtotal * tax.amount / 100, 2)),
                    "tributo_codigo": str(tax.tax_group_id.code),
                    "tributo_nombre": str(tax.tax_group_id.description),
                    "tributo_tipo_codigo": str(tax.tax_group_id.name_code),
                    "TierRange": "01"
                }
                subtotal_tax = subtotal_tax + round(subtotal * tax.amount / 100, 2)
                TaxTotals.append(taxDict)

            # if len(TaxTotals) < 2: str(line.product_id.id), line.name

            debit_note_line = NotaDebitoObject.DebitNoteLine(line_id=str(line_id), line_debited_quantity=str(round(line.quantity,2)),
                                                             line_extension_amount=str(round(line.price_subtotal,2)),
                                                            price_amount=str(line.product_id.lst_price), price_type_code="01",
                                                            tax_exemption_code=str(line.tipo_afectacion_igv.code), tax_amount= str(round(subtotal*tax.amount/100,2)),
                                                            description=line.name, sellers_id=str(line.product_id.id),
                                                             line_price_amount=str(line.product_id.lst_price), array_tax_totals=TaxTotals,
                                                             currency_id=self.company_id.currency_id.name,unit_code=str(line.uom_id.code))
            line_id = line_id + 1
            nota_debito.appendChild(debit_note_line)

        I = nota_debito.toprettyxml("        ")
        self.write({"documentoXML": I})
