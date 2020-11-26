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


class accountJournal(models.Model):
    _inherit = "account.journal"

    def _list_invoice_type(self):
        catalogs = self.env["einvoice.catalog.01"].search([])
        list = []
        for cat in catalogs:
            list.append((cat.code, cat.name))
        return list

    codigo_documento = fields.Char("Codigo de tipo de Documento")
    invoice_type_code_id = fields.Selection(
        string="Tipo de Documento", selection=_list_invoice_type
    )

