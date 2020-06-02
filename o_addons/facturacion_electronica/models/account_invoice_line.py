#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from utils.InvoiceLine import Factura
from suds.client import Client
from suds.wsse import *
from signxml import XMLSigner, XMLVerifier, methods
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import xml.etree.ElementTree as ET
import requests
import zipfile
import base64
import os
import logging


class accountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _tipo_afectacion_igv(self):
        return self.env["einvoice.catalog.07"].search([["code", "=", 10]])

    tipo_afectacion_igv = fields.Many2one(
        "einvoice.catalog.07", default=_tipo_afectacion_igv
    )
    no_onerosa = fields.Boolean(
        related="tipo_afectacion_igv.no_onerosa", string="No Oneroso"
    )

    tipo_sistema_calculo_isc = fields.Many2one("einvoice.catalog.08")
    invoice_line_tax_ids = fields.Many2many(
        "account.tax",
        "account_invoice_line_tax",
        "invoice_line_id",
        "tax_id",
        string="Taxes",
        domain=[
            ("type_tax_use", "!=", "none"),
            "|",
            ("active", "=", False),
            ("active", "=", True),
        ],
        oldname="invoice_line_tax_id",
        compute="_change_tipo_afectacion_igv",
    )

    @api.one
    @api.depends("tipo_afectacion_igv")
    def _change_tipo_afectacion_igv(self):
        if self.invoice_id.type != "in_invoice":
            if self.tipo_afectacion_igv.no_onerosa:
                self.invoice_line_tax_ids.unlink()
            else:
                taxes_id = [tax_id.id for tax_id in self.product_id.taxes_id]
                self.invoice_line_tax_ids = [(6, 0, taxes_id)]
            # self._compute_price()
        else:
            taxes_id = [tax_id.id for tax_id in self.product_id.supplier_taxes_id]
            print("product taxes")
            print(taxes_id)
            self.invoice_line_tax_ids = [(6, 0, taxes_id)]
        self._compute_price()
