#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from odoo.tools.safe_eval import safe_eval
#from utils.InvoiceLine import Factura
from suds.client import Client
from suds.wsse import *
from signxml import XMLSigner, XMLVerifier,methods
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import xml.etree.ElementTree as ET
import requests
import zipfile
import base64
import os
import logging
'''import sys
sys.path.insert(0, 'utils/InvoiceLine')'''

class accountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    code = fields.Char("Codigo",required=True)
    description = fields.Char("Descripcion",required=True)
    name_code = fields.Char("Nombre del Codigo",required=True)