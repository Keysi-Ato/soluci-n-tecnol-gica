# -*- coding: utf-8 -*-
#import number_to_letter
from odoo import models, api
#
#class StockPicking2(models.Model):
    #_inherit = "stock.picking"

     #@api.multi
     #def do_print_picking(self):
        #self.write({'printed': True})
        #return self.env.ref('stock.action_report_guia_remi').report_action(self)


class StockReportGuiaRemitente(models.AbstractModel):
    #_name = 'report.stock.report_guia_remitente'
    _name = 'report.report_number_to_letter.report_guia_remitente_document'
    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        #report = report_obj._get_report_from_name('stock.report_guia_remitente')
        #docs = self.env[report.model].browse(docids)
        doc = self.env['stock.picking'].browse(docids)
        factura = self.env['account.invoice'].search([["origin", "=", doc.origin]])
        almacen = self.env['stock.warehouse'].search([("partner_id", "=", doc.company_id.partner_id.id)])
        
        docargs = {
            'doc_ids': doc, #self.ids,
            'factura': factura,
            'almacen': almacen,
            'doc_model': 'stock.picking',
        }
        return report_obj.render('report_number_to_letter.report_guia_remitente_document', docargs)
        #return docargs