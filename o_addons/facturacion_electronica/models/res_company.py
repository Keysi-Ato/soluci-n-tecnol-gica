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
import requests
import logging

class resCompany(models.Model):
    _inherit = "res.company"
    
    private=fields.Text("Clave Privada")
    public=fields.Text("Clave Publica")
    sunat_username=fields.Char("Usuario SOL")
    sunat_password=fields.Char("Password SOL")
    send_route = fields.Selection([
        ('https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService','Servidor Beta'),
        ('https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService','Servidor de producción')
        ], string="Ruta de envío")