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


class invoice_boleta(models.Model):
    _inherit = "account.invoice"
    @api.multi
    def generarBoletaVenta(self):
        BoletaVentaObject=Boleta()
        # Invoice = BoletaVentaObject.Root()

        Invoice = BoletaVentaObject.SummaryRoot(ubl_version_id="2.0", customization_id="1.0", summary_id=str(self.number),
                            reference_data="2018-01-23", issue_date=str(self.date_invoice), note="Note 1")
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

            summary_line = BoletaVentaObject.SummaryLine(line_id=str(line_id), document_type=str(subtotal),
                                                         document_serial="DA45", start_document="456", end_document="764",
                                                         total_amount="117350.75", paid_amount=["78223.00", "24423.00", "0.00"],
                                                         tax_id="01", charge_indicator="true", amount="0.00",
                                                         array_tax_sub_total=TaxTotals)
            line_id = line_id + 1
            Invoice.appendChild(summary_line)

        # Invoice.appendChild(root)
        I = Invoice.toprettyxml("        ")
        self.write({"documentoXML": I})
