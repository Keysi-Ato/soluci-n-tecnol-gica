#!/usr/bin/env python
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.http import request
from odoo.tools.float_utils import float_compare
from suds.client import Client  #para exportar y la firma 
from suds.wsse import * #para exportar y la firmaa
from signxml import XMLSigner, XMLVerifier, methods  #para exportar y la firmaa
from datetime import datetime, timedelta
from io import StringIO
import xlwt, xlsxwriter
from xlwt import easyxf
import xml.etree.ElementTree as ET
import requests
import zipfile
import base64

import os
import logging
import json
import math
import time
import calendar


class ActivosFijos(models.Model):
    _name = "account.activos"

    codigo = fields.Text("Código")
    descripcion = fields.Text("Descripción")
    marca = fields.Text("Marca de activo fijo")
    modelo = fields.Text("Modelo del activo fijo")
    serie = fields.Text("Número de serie y/o placa del activo fijo")
    saldo = fields.Float("Saldo inicial")
    adquisicion = fields.Text("Adquisiciones")
    mejora = fields.Text("Mejoras")
    retiro = fields.Text("Retiros y/o bajas")
    otros = fields.Text("Otros ajustes")
    historico = fields.Text("Valor histórico")
    inflacion = fields.Text("Ajuste por inflación")
    ajustado = fields.Text("Valor ajustado")
    fecha_adq = fields.Date("Fecha de adquisición")
    fecha_uso = fields.Date("Fecha de inicio de uso")
    metodo = fields.Text("Método aplicado")
    n_documento = fields.Text("Nro. de documento de autorización")
    porcentaje = fields.Float("Porcentaje de depreciación")
    acumulada = fields.Text("Depreciación acumulada al cierre del ejercicio anterior")
    depreciacion = fields.Text("Depreciación del ejercicio")
    depreciacion_retiro = fields.Text(
        "Depreciación  del ejercicio relacionada con retiros y/o bajas"
    )
    depreciacion_otros = fields.Text("Depreciación relacionada con otros ajustes")
    depreciacion_acumulada = fields.Text("Depreciación acumulada histórica")
    depreciacion_ajuste = fields.Text("Ajuste por inflación de la depreciación")
    depreciacion_acumulada_ajustada = fields.Text(
        "Depreciación acumulada ajustada por inflación"
    )

# REGISTRO DE COMPRAS
class PrintReportTextCompras(models.TransientModel):
    _name = "print.compras.reporte.contabilidad"

    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list

    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Reporte de Compras")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Reporte de Compras")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )
    tipo_reporte = fields.Boolean(string="Archivo txt?", default=False)

    @api.multi
    def generaReporte(self):
        monthRange = calendar.monthrange(int(self.years), int(self.months))

        invoice_objs = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.years + "-" + self.months + "-01"),
                (
                    "date_invoice",
                    "<=",
                    self.years + "-" + self.months + "-" + str(monthRange[1]),
                ),
                ("type", "=", "in_invoice"),
                ("state", "not in", ["draft", "cancel"]),
            ]
        )

        tipo_reporte = self.tipo_reporte

        for wizard in self:
            if tipo_reporte:
                fp = StringIO()
                cuo = 1
                for line in invoice_objs:
                    di = datetime.strptime(line.date_invoice, "%Y-%m-%d")
                    di = unicode(di.date()).split("-")
                    fdi = "/".join(reversed(di))

                    if line.date_due is False:
                        dd = line.date_invoice
                    else:
                        dd = line.date_due
                    # Por mientras
                    dd = ""

                    if line.partner_id.parent_id:
                        doccode = line.partner_id.parent_id.catalog_06_id.code
                        vatcode = line.partner_id.parent_id.vat
                        docname = line.partner_id.parent_id.name
                    else:
                        doccode = line.partner_id.catalog_06_id.code
                        vatcode = line.partner_id.vat
                        docname = line.partner_id.name
                    ac = "M" + unicode(cuo).zfill(3)

                    if line.reference is False:
                        reference = "0-0"
                    else:
                        reference = line.reference

                    compras = (
                        self.years
                        + self.months
                        + "00"
                        + "|"
                        + unicode(cuo)
                        + "|"
                        + unicode(ac)
                        + "|"
                        + unicode(fdi)
                        + "|"
                        + unicode(dd)
                        + "|"
                        + unicode(line.tipo_documento)
                        + "|"
                        + unicode(reference.split("-")[0])
                        + "|"
                        + ""
                        + "|"
                        + unicode(reference.split("-")[1])
                        + "|"
                        + ""
                        + "|"
                        + unicode(line.partner_id.catalog_06_id.code)
                        + "|"
                        + unicode(line.partner_id.vat)
                        + "|"
                        + unicode(line.partner_id.name)
                        + "|"
                        + unicode(line.amount_untaxed)
                        + "|"
                        + unicode(line.amount_tax)
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + unicode(line.amount_total)
                        + "|"
                        + unicode(line.currency_id.name)
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + "1"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + "1"
                        + "\n"
                    )

                    fp.write(compras.encode("utf-8"))
                    cuo = cuo + 1

                file_text_name = (
                    "LE"
                    + self.create_uid.company_id.vat
                    + self.years
                    + self.months
                    + "0008010000"
                    + "1111.txt"
                )

                excel_file = base64.encodestring(fp.getvalue())
                wizard.invoice_summary_file = excel_file
                # wizard.file_name = "Compras.txt"
                wizard.file_name = file_text_name
                wizard.invoice_report_printed = True
                fp.close()

                return {
                    "view_mode": "form",
                    "res_id": wizard.id,
                    "res_model": "print.compras.reporte.contabilidad",
                    "view_type": "form",
                    "type": "ir.actions.act_window",
                    "context": wizard.env.context,
                    "target": "new",
                }
            else:
                workbook = xlwt.Workbook()
                amount_tot = 0
                column_heading_style = easyxf("font:height 200;font:bold True;")
                worksheet = workbook.add_sheet("Compras")
                worksheet.write(
                    2,
                    5,
                    self.env.user.company_id.name,
                    easyxf("font:height 200;font:bold True;align: horiz center;"),
                )
                worksheet.write(6, 0, _("Periodo"), column_heading_style)
                worksheet.write(6, 1, _("Fecha"), column_heading_style)
                worksheet.write(6, 2, _("Tipo de documento"), column_heading_style)
                worksheet.write(6, 3, _("Serie"), column_heading_style)
                worksheet.write(6, 4, _("Número"), column_heading_style)
                worksheet.write(6, 5, _("RUC"), column_heading_style)
                worksheet.write(6, 6, _("Cliente"), column_heading_style)
                worksheet.write(6, 7, _("Monto sin impuesto"), column_heading_style)
                worksheet.write(6, 8, _("Impuesto"), column_heading_style)
                worksheet.write(6, 9, _("Total"), column_heading_style)

                worksheet.col(0).width = 5000
                worksheet.col(1).width = 5000
                worksheet.col(2).width = 5000
                worksheet.col(3).width = 5000
                worksheet.col(4).width = 5000
                worksheet.col(5).width = 5000
                worksheet.col(6).width = 5000
                worksheet.col(7).width = 5000
                worksheet.col(8).width = 5000
                worksheet.col(9).width = 5000

                row = 7
                customer_row = 2
                for wizard in self:
                    customer_payment_data = {}
                    heading = "Ventas"
                    worksheet.write_merge(
                        0,
                        0,
                        0,
                        9,
                        heading,
                        easyxf(
                            "font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;"
                            "borders: top thin,bottom thin"
                        ),
                    )

                    for line in invoice_objs:
                        di = datetime.strptime(line.date_invoice, "%Y-%m-%d")
                        di = unicode(di.date()).split("-")
                        fdi = "/".join(reversed(di))

                        if line.date_due is False:
                            dd = line.date_invoice
                        else:
                            dd = line.date_due
                        # Por mientras
                        dd = ""

                        if line.partner_id.parent_id:
                            doccode = line.partner_id.parent_id.catalog_06_id.code
                            vatcode = line.partner_id.parent_id.vat
                            docname = line.partner_id.parent_id.name
                        else:
                            doccode = line.partner_id.catalog_06_id.code
                            vatcode = line.partner_id.vat
                            docname = line.partner_id.name

                        if line.reference is False:
                            reference = "0-0"
                        else:
                            reference = line.reference

                        worksheet.write(row, 0, self.years + self.months + "00")
                        worksheet.write(row, 1, fdi)
                        worksheet.write(row, 2, line.tipo_documento)
                        worksheet.write(row, 3, reference.split("-")[0])
                        worksheet.write(row, 4, reference.split("-")[1])
                        worksheet.write(row, 5, vatcode)
                        worksheet.write(row, 6, docname)
                        worksheet.write(row, 7, line.amount_untaxed)
                        worksheet.write(row, 8, line.amount_tax)
                        worksheet.write(row, 9, line.amount_total)

                        row += 1

                    fp = StringIO()
                    workbook.save(fp)
                    excel_file = base64.encodestring(fp.getvalue())
                    wizard.invoice_summary_file = excel_file
                    wizard.file_name = "Reporte de Compras.xls"
                    wizard.invoice_report_printed = True
                    fp.close()
                    return {
                        "view_mode": "form",
                        "res_id": wizard.id,
                        "res_model": "print.compras.reporte.contabilidad",
                        "view_type": "form",
                        "type": "ir.actions.act_window",
                        "context": self.env.context,
                        "target": "new",
                    }


# REGISTRO DE VENTAS
class PrintReportTextVentas(models.TransientModel):
    _name = "print.ventas.reporte.contabilidad"

    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list

    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Reporte de Ventas")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Reporte de Ventas")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )
    tipo_reporte = fields.Boolean(string="Archivo txt?", default=False)

    @api.multi
    def generaReporte(self):
        monthRange = calendar.monthrange(int(self.years), int(self.months))

        invoice_objs = self.env["account.invoice"].search(
            [
                ("date_invoice", ">=", self.years + "-" + self.months + "-01"),
                (
                    "date_invoice",
                    "<=",
                    self.years + "-" + self.months + "-" + str(monthRange[1]),
                ),
                ("type", "=", "out_invoice"),
                ("state", "not in", ["draft", "cancel"]),
            ]
        )

        tipo_reporte = self.tipo_reporte

        for wizard in self:
            if tipo_reporte:
                fp = StringIO()
                cuo = 1
                for line in invoice_objs:
                    di = datetime.strptime(line.date_invoice, "%Y-%m-%d")
                    di = unicode(di.date()).split("-")
                    fdi = "/".join(reversed(di))

                    if line.date_due is False:
                        dd = line.date_invoice
                    else:
                        dd = line.date_due
                    # Por mientras
                    dd = ""

                    if line.partner_id.parent_id:
                        doccode = line.partner_id.parent_id.catalog_06_id.code
                        vatcode = line.partner_id.parent_id.vat
                        docname = line.partner_id.parent_id.name
                    else:
                        doccode = line.partner_id.catalog_06_id.code
                        vatcode = line.partner_id.vat
                        docname = line.partner_id.name
                    ac = "M" + unicode(cuo).zfill(3)

                    ventas = (
                        self.years
                        + self.months
                        + "00"
                        + "|"
                        + unicode(cuo)
                        + "|"
                        + unicode(ac)
                        + "|"
                        + unicode(fdi)
                        + "|"
                        + unicode(dd)
                        + "|"
                        + unicode(line.tipo_documento)
                        + "|"
                        + unicode(line.number.split("-")[0])
                        + "|"
                        + unicode(line.number.split("-")[1])
                        + "|"
                        + ""
                        + "|"
                        + unicode(doccode)
                        + "|"
                        + unicode(vatcode)
                        + "|"
                        + unicode(docname)
                        + "|"
                        + ""
                        + "|"
                        + unicode(line.amount_untaxed)
                        + "|"
                        + ""
                        + "|"
                        + unicode(line.amount_tax)
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + unicode(line.amount_total)
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + ""
                        + "|"
                        + "1"
                        + "|"
                        + "1"
                        + "|"
                        + ""
                        + "\n"
                    )

                    fp.write(ventas.encode("utf-8"))
                    cuo = cuo + 1

                file_text_name = (
                    "LE"
                    + self.create_uid.company_id.vat
                    + self.years
                    + self.months
                    + "0014010000"
                    + "1111.txt"
                )
                excel_file = base64.encodestring(fp.getvalue())
                wizard.invoice_summary_file = excel_file
                # wizard.file_name = "Ventas.txt"
                wizard.file_name = file_text_name
                wizard.invoice_report_printed = True
                fp.close()

                return {
                    "view_mode": "form",
                    "res_id": wizard.id,
                    "res_model": "print.ventas.reporte.contabilidad",
                    "view_type": "form",
                    "type": "ir.actions.act_window",
                    "context": wizard.env.context,
                    "target": "new",
                }
            else:
                workbook = xlwt.Workbook()
                amount_tot = 0
                column_heading_style = easyxf("font:height 200;font:bold True;")
                worksheet = workbook.add_sheet("Ventas")
                worksheet.write(
                    2,
                    5,
                    self.env.user.company_id.name,
                    easyxf("font:height 200;font:bold True;align: horiz center;"),
                )
                worksheet.write(6, 0, _("Periodo"), column_heading_style)
                worksheet.write(6, 1, _("Fecha"), column_heading_style)
                worksheet.write(6, 2, _("Tipo de documento"), column_heading_style)
                worksheet.write(6, 3, _("Serie"), column_heading_style)
                worksheet.write(6, 4, _("Número"), column_heading_style)
                worksheet.write(6, 5, _("RUC"), column_heading_style)
                worksheet.write(6, 6, _("Cliente"), column_heading_style)
                worksheet.write(6, 7, _("Monto sin impuesto"), column_heading_style)
                worksheet.write(6, 8, _("Impuesto"), column_heading_style)
                worksheet.write(6, 9, _("Total"), column_heading_style)

                worksheet.col(0).width = 5000
                worksheet.col(1).width = 5000
                worksheet.col(2).width = 5000
                worksheet.col(3).width = 5000
                worksheet.col(4).width = 5000
                worksheet.col(5).width = 5000
                worksheet.col(6).width = 5000
                worksheet.col(7).width = 5000
                worksheet.col(8).width = 5000
                worksheet.col(9).width = 5000

                row = 7
                customer_row = 2
                for wizard in self:
                    customer_payment_data = {}
                    heading = "Ventas"
                    worksheet.write_merge(
                        0,
                        0,
                        0,
                        9,
                        heading,
                        easyxf(
                            "font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;"
                            "borders: top thin,bottom thin"
                        ),
                    )

                    for line in invoice_objs:
                        di = datetime.strptime(line.date_invoice, "%Y-%m-%d")
                        di = unicode(di.date()).split("-")
                        fdi = "/".join(reversed(di))

                        if line.date_due is False:
                            dd = line.date_invoice
                        else:
                            dd = line.date_due
                        # Por mientras
                        dd = ""

                        if line.partner_id.parent_id:
                            doccode = line.partner_id.parent_id.catalog_06_id.code
                            vatcode = line.partner_id.parent_id.vat
                            docname = line.partner_id.parent_id.name
                        else:
                            doccode = line.partner_id.catalog_06_id.code
                            vatcode = line.partner_id.vat
                            docname = line.partner_id.name
                        worksheet.write(row, 0, self.years + self.months + "00")
                        worksheet.write(row, 1, fdi)
                        worksheet.write(row, 2, line.tipo_documento)
                        worksheet.write(row, 3, line.number.split("-")[0])
                        worksheet.write(row, 4, line.number.split("-")[1])
                        worksheet.write(row, 5, vatcode)
                        worksheet.write(row, 6, docname)
                        worksheet.write(row, 7, line.amount_untaxed)
                        worksheet.write(row, 8, line.amount_tax)
                        worksheet.write(row, 9, line.amount_total)

                        row += 1

                    fp = StringIO()
                    workbook.save(fp)
                    excel_file = base64.encodestring(fp.getvalue())
                    wizard.invoice_summary_file = excel_file
                    wizard.file_name = "Reporte de Ventas.xls"
                    wizard.invoice_report_printed = True
                    fp.close()
                    return {
                        "view_mode": "form",
                        "res_id": wizard.id,
                        "res_model": "print.ventas.reporte.contabilidad",
                        "view_type": "form",
                        "type": "ir.actions.act_window",
                        "context": self.env.context,
                        "target": "new",
                    }


# REGISTRO DIARIO
class PrintReportTextDiario(models.TransientModel):
    _name = "print.diario.reporte.contabilidad"

    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list

    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Reporte de Diario")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Reporte de Diario")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )

    @api.multi
    def generaReporte(self):
        monthRange = calendar.monthrange(int(self.years), int(self.months))

        invoice_objs = self.env["account.move.line"].search(
            [
                ("date", ">=", self.years + "-" + self.months + "-01"),
                ("date", "<=", self.years + "-" + self.months + "-" + str(monthRange[1])),
            ]
        )

        for wizard in self:
            fp = StringIO()
            cuo = 1
            for line in invoice_objs:
                di = datetime.strptime(line.date, "%Y-%m-%d")
                di = unicode(di.date()).split("-")
                fdi = "/".join(reversed(di))

                if line.date_maturity is False:
                    dd = line.date
                else:
                    dd = line.date_maturity

                if line.move_id.name.find("-") > 0:
                    documento = self.env["account.invoice"].search(
                        [("number", "=", line.move_id.name)]
                    )

                    tipo = documento.tipo_documento
                    serie = documento.number.split("-")[0]
                    numero = documento.number.split("-")[1]
                else:
                    tipo = ""
                    serie = ""
                    numero = ""

                ac = "M" + unicode(cuo).zfill(3)
                diario = (
                    self.years
                    + self.months
                    + "00"
                    + "|"
                    + unicode(cuo)
                    + "|"
                    + unicode(ac)
                    + "|"
                    + unicode(line.account_id.code)
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.move_id.name)
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + unicode(tipo)
                    + "|"
                    + unicode(serie)
                    + "|"
                    + unicode(numero)
                    + "|"
                    + unicode(fdi)
                    + "|"
                    + unicode(dd).replace("-", "/")
                    + "|"
                    + unicode(fdi)
                    + "|"
                    + unicode(line.name)
                    + "|"
                    + ""
                    + "|"
                    + unicode(line.debit)
                    + "|"
                    + unicode(line.credit)
                    + "|"
                    + ""
                    + "|"
                    + "1"
                    + "|"
                    + ""
                    + "\n"
                )

                fp.write(diario.encode("utf-8"))
                cuo = cuo + 1

            # LERRRRRRRRRRRAAAAMM0005020000OIM1.TXT
            file_text_name = (
                "LE"
                + self.create_uid.company_id.vat
                + self.years
                + self.months
                + "0005020000"
                + "1111.txt"
            )
            excel_file = base64.encodestring(fp.getvalue())
            wizard.invoice_summary_file = excel_file
            # wizard.file_name = "Diario_ventas.txt"
            wizard.file_name = file_text_name
            wizard.invoice_report_printed = True
            fp.close()

            return {
                "view_mode": "form",
                "res_id": wizard.id,
                "res_model": "print.diario.reporte.contabilidad",
                "view_type": "form",
                "type": "ir.actions.act_window",
                "context": wizard.env.context,
                "target": "new",
            }


# PLAN CONTABLE
class PrintReportPlanContable(models.TransientModel):
    _name = "print.plancontable.reporte.contabilidad"

    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list

    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Plan Contable")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Plan contable")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )

    @api.multi
    def generaReporte(self):
        plan_object = self.env["account.account"].search([])

        for wizard in self:
            fp = StringIO()

            for line in plan_object:
                plan = (
                    self.years
                    + self.months
                    + "00"
                    + "|"
                    + unicode(line.code)
                    + "|"
                    + unicode(line.name)
                    + "|"
                    + "01"
                    + "|"
                    + "-"
                    + "|"
                    + ""
                    + "|"
                    + ""
                    + "|"
                    + "1"
                    + "\n"
                )

                fp.write(plan.encode("utf-8"))

            # LERRRRRRRRRRRAAAAMM0005040000OIM1.TXT
            file_text_name = (
                "LE"
                + self.create_uid.company_id.vat
                + self.years
                + self.months
                + "0005040000"
                + "1111.txt"
            )
            excel_file = base64.encodestring(fp.getvalue())
            wizard.invoice_summary_file = excel_file
            # wizard.file_name = "Plan_contable.txt"
            wizard.file_name = file_text_name
            wizard.invoice_report_printed = True
            fp.close()

            return {
                "view_mode": "form",
                "res_id": wizard.id,
                "res_model": "print.plancontable.reporte.contabilidad",
                "view_type": "form",
                "type": "ir.actions.act_window",
                "context": wizard.env.context,
                "target": "new",
            }


class PrintActivosFijos(models.TransientModel):
    _name = "print.account.activos.fijos"
    
    def _list_anios(self):
        d = datetime.now()

        list = []

        i = 0
        while i < 3:
            anios = timedelta(days=365 * i)
            reference_date = d - anios
            list.append((str(reference_date.year), str(reference_date.year)))
            i += 1

        return list
    def get_month(self):
        d = datetime.now()
        return "{:02d}".format(d.month)

    def get_year(self):
        d = datetime.now()
        return "{:04d}".format(d.year)

    invoice_summary_file = fields.Binary("Activos Fijos")
    file_name = fields.Char("File Name")
    invoice_report_printed = fields.Boolean("Activos Fijos")
    years = fields.Selection(string="Año", selection=_list_anios, default=get_year)
    months = fields.Selection(
        string="Mes",
        selection=[
            ("01", "Enero"),
            ("02", "Febrero"),
            ("03", "Marzo"),
            ("04", "Abril"),
            ("05", "Mayo"),
            ("06", "Junio"),
            ("07", "Julio"),
            ("08", "Agosto"),
            ("09", "Septiembre"),
            ("10", "Octubre"),
            ("11", "Noviembre"),
            ("12", "Diciembre"),
        ],
        default=get_month,
    )
    tipo_reporte = fields.Boolean(string="Archivo txt?", default=False)
    
    @api.multi
    def generaReporte(self):
        tipo_reporte = self.tipo_reporte

        invoice_objs = self.env["account.activos"].search([])

        for wizard in self:
            if tipo_reporte:
                fp = StringIO()
                cuo = 1
                for line in invoice_objs:
                    di = datetime.strptime(line.date_invoice, "%Y-%m-%d")
                    di = unicode(di.date()).split("-")
                    fdi = "/".join(reversed(di))

                    if line.date_due is False:
                        dd = line.date_invoice
                    else:
                        dd = line.date_due
                    # Por mientras
                    dd = ""

                    if line.partner_id.parent_id:
                        doccode = line.partner_id.parent_id.catalog_06_id.code
                        vatcode = line.partner_id.parent_id.vat
                        docname = line.partner_id.parent_id.name
                    else:
                        doccode = line.partner_id.catalog_06_id.code
                        vatcode = line.partner_id.vat
                        docname = line.partner_id.name
                    ac = "M" + unicode(cuo).zfill(3)

                    ventas = (
                        self.years
                        + self.months
                        + "00"
                        + "|"
                        + unicode(cuo)
                        + "|"
                        + unicode(ac)
                        + "|"
                        + "tabla13"
                        + "|"
                        + "catalagocampo4"
                        + "|"
                        + ""
                        + "|"
                        + "tabla18"
                        + "|"
                        + "CUENTACONTABLE"
                        + "|"
                        + "ESTADO TABLA 19"
                        + "|"
                        + unicode(line.descripcion)
                        + "|"
                        + unicode(line.marca)
                        + "|"
                        + unicode(line.modelo)
                        + "|"
                        + unicode(line.serie)
                        + "|"
                        + unicode(line.saldo)
                        + "|"
                        + unicode(line.adquisicion)
                        + "|"
                        + unicode(line.mejora)
                        + "|"
                        + unicode(line.retiro)
                        + "|"
                        + unicode(line.otros)
                        + "|"
                        + "VALOR DE REEVALUACION VOLUNTARIO"
                        + "|"
                        + "VALOR DE REEVALUACION DE SOCIEDADES"
                        + "|"
                        + "VALOR DE REEVALUACION EFECTUADA"
                        + "|"
                        + unicode(line.inflacion)
                        + "|"
                        + unicode(line.fecha_adq)
                        + "|"
                        + unicode(line.fecha_uso)
                        + "|"
                        + unicode(line.metodo)
                        + "|"
                        + unicode(line.n_documento)
                        + "|"
                        + unicode(line.porcentaje)
                        + "|"
                        + unicode(line.acumulada)
                        + "|"
                        + unicode(line.depreciacion)
                        + "|"
                        + unicode(line.depreciacion_retiro)
                        + "|"
                        + unicode(line.depreciacion_otros)
                        + "|"
                        + "VALOR DE DEPRECIACION REVALUACION VOLUNTARIA EFECTUADA"
                        + "|"
                        + "VALOR DE DEPRECIACION REVALUACION EFECTUADA X REORGANIZACION"
                        + "|"
                        + "VALOR DE DEPRECIACION OTRAS REVALUACIONES EFECTUADA"
                        + "|"
                        + unicode(line.depreciacion_ajuste)
                        + "|"
                        + "1"
                        + "\n"
                    )

                    fp.write(ventas.encode("utf-8"))
                    cuo = cuo + 1

                file_text_name = (
                    "LE"
                    + self.create_uid.company_id.vat
                    + self.years
                    + "000007010000"
                    + "1111.txt"
                )

                excel_file = base64.encodestring(fp.getvalue())
                wizard.invoice_summary_file = excel_file
                wizard.file_name = file_text_name
                wizard.invoice_report_printed = True
                fp.close()

                return {
                    "view_mode": "form",
                    "res_id": wizard.id,
                    "res_model": "print.account.activos.fijos",
                    "view_type": "form",
                    "type": "ir.actions.act_window",
                    "context": wizard.env.context,
                    "target": "new",
                }
            else:
                workbook = xlwt.Workbook()
                amount_tot = 0
                column_heading_style = easyxf("font:height 200;font:bold True;")
                worksheet = workbook.add_sheet("Activos Fijos")
                worksheet.write(
                    2,
                    5,
                    self.env.user.company_id.name,
                    easyxf("font:height 200;font:bold True;align: horiz center;"),
                )

                worksheet.write(6, 0, _("Código"), column_heading_style)
                worksheet.write(6, 1, _("Descripción"), column_heading_style)
                worksheet.write(6, 2, _("Marca de activo fijo"), column_heading_style)
                worksheet.write(6, 3, _("Modelo del activo fijo"), column_heading_style)
                worksheet.write(
                    6,
                    4,
                    _("Número de serie y/o placa del activo fijo"),
                    column_heading_style,
                )
                worksheet.write(6, 5, _("Saldo inicial"), column_heading_style)
                worksheet.write(6, 6, _("Adquisiciones"), column_heading_style)
                worksheet.write(6, 7, _("Mejoras"), column_heading_style)
                worksheet.write(6, 8, _("Retiros y/o bajas"), column_heading_style)
                worksheet.write(6, 9, _("Otros ajustes"), column_heading_style)
                worksheet.write(6, 10, _("Valor histórico"), column_heading_style)
                worksheet.write(6, 11, _("Ajuste por inflación"), column_heading_style)
                worksheet.write(6, 12, _("Valor ajustado"), column_heading_style)
                worksheet.write(6, 13, _("Fecha de adquisición"), column_heading_style)
                worksheet.write(6, 14, _("Fecha de inicio de uso"), column_heading_style)
                worksheet.write(6, 15, _("Método aplicado"), column_heading_style)
                worksheet.write(
                    6, 16, _("Nro. de documento de autorización"), column_heading_style
                )
                worksheet.write(
                    6, 17, _("Porcentaje de depreciación"), column_heading_style
                )
                worksheet.write(
                    6,
                    18,
                    _("Depreciación acumulada al cierre del ejercicio anterior"),
                    column_heading_style,
                )
                worksheet.write(
                    6, 19, _("Depreciación del ejercicio"), column_heading_style
                )
                worksheet.write(
                    6,
                    20,
                    _("Depreciación  del ejercicio relacionada con retiros y/o bajas"),
                    column_heading_style,
                )
                worksheet.write(
                    6,
                    21,
                    _("Depreciación relacionada con otros ajustes"),
                    column_heading_style,
                )
                worksheet.write(
                    6, 22, _("Depreciación acumulada histórica"), column_heading_style
                )
                worksheet.write(
                    6,
                    23,
                    _("Ajuste por inflación de la depreciación"),
                    column_heading_style,
                )
                worksheet.write(
                    6,
                    24,
                    _("Depreciación acumulada ajustada por inflación"),
                    column_heading_style,
                )

                worksheet.col(0).width = 5000
                worksheet.col(1).width = 5000
                worksheet.col(2).width = 5000
                worksheet.col(3).width = 5000
                worksheet.col(4).width = 5000
                worksheet.col(5).width = 5000
                worksheet.col(6).width = 5000
                worksheet.col(7).width = 5000
                worksheet.col(8).width = 5000
                worksheet.col(9).width = 5000
                worksheet.col(10).width = 5000
                worksheet.col(11).width = 5000
                worksheet.col(12).width = 5000
                worksheet.col(13).width = 5000
                worksheet.col(14).width = 5000
                worksheet.col(15).width = 5000
                worksheet.col(16).width = 5000
                worksheet.col(17).width = 5000
                worksheet.col(18).width = 5000
                worksheet.col(19).width = 5000
                worksheet.col(20).width = 5000
                worksheet.col(21).width = 5000
                worksheet.col(22).width = 5000
                worksheet.col(23).width = 5000
                worksheet.col(24).width = 5000

                row = 7
                customer_row = 2

                for wizard in self:
                    customer_payment_data = {}
                    heading = "Activos fijos"
                    worksheet.write_merge(
                        0,
                        0,
                        0,
                        14,
                        heading,
                        easyxf(
                            "font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;"
                            "borders: top thin,bottom thin"
                        ),
                    )

                    for line in invoice_objs:
                        worksheet.write(row, 0, line.codigo)
                        worksheet.write(row, 1, line.descripcion)
                        worksheet.write(row, 2, line.marca)
                        worksheet.write(row, 3, line.modelo)
                        worksheet.write(row, 4, line.serie)
                        worksheet.write(row, 5, line.saldo)
                        worksheet.write(row, 6, line.adquisicion)
                        worksheet.write(row, 7, line.mejora)
                        worksheet.write(row, 8, line.retiro)
                        worksheet.write(row, 9, line.otros)
                        worksheet.write(row, 10, line.historico)
                        worksheet.write(row, 11, line.inflacion)
                        worksheet.write(row, 12, line.ajustado)
                        worksheet.write(row, 13, line.fecha_adq)
                        worksheet.write(row, 14, line.fecha_uso)
                        worksheet.write(row, 15, line.metodo)
                        worksheet.write(row, 16, line.n_documento)
                        worksheet.write(row, 17, line.porcentaje)
                        worksheet.write(row, 18, line.acumulada)
                        worksheet.write(row, 19, line.depreciacion)
                        worksheet.write(row, 20, line.depreciacion_retiro)
                        worksheet.write(row, 21, line.depreciacion_otros)
                        worksheet.write(row, 22, line.depreciacion_acumulada)
                        worksheet.write(row, 23, line.depreciacion_ajuste)
                        worksheet.write(row, 24, line.depreciacion_acumulada_ajustada)

                        row += 1

                    fp = StringIO()
                    workbook.save(fp)
                    excel_file = base64.encodestring(fp.getvalue())
                    wizard.invoice_summary_file = excel_file
                    wizard.file_name = "Activos fijos.xls"
                    wizard.invoice_report_printed = True
                    fp.close()
                    return {
                        "view_mode": "form",
                        "res_id": wizard.id,
                        "res_model": "print.account.activos.fijos",
                        "view_type": "form",
                        "type": "ir.actions.act_window",
                        "context": self.env.context,
                        "target": "new",
                    }
    