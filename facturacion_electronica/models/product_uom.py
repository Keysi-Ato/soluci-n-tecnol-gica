#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from odoo.tools.safe_eval import safe_eval
from utils.InvoiceLine import Factura
from suds.client import Client
from suds.wsse import *
from signxml import XMLSigner, XMLVerifier,methods
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import xml.etree.ElementTree as ET
import requests
import zipfile
import base64
import os
import requests
import logging

class productUom(models.Model):
    _inherit = "product.uom"
    
    code=fields.Char(string="Codigo")
    description=fields.Char(string="Descripcion")