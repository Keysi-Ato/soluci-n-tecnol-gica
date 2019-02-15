# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.http import request

class SaleOrder(models.Model):
    _inherit = "sale.order"

    tipo_documento = fields.Selection(string="Tipo de Documento",selection=[('01','Factura'),('03','Boleta')], required=True, default='01')

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            # action['domain'] = [('journal_id.invoice_type_code_id','=','01')]
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
            
            default_journal_id = self.env["account.journal"].search([["invoice_type_code_id", "=", self.tipo_documento]])
            action["context"] = "{'type_code':'"+self.tipo_documento+"'}"
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

#   [('type','in',('out_invoice', 'out_refund')),('journal_id.invoice_type_code_id','=','01')]            
    # @api.multi
    # def action_view_invoice(self):
    #     invoices = self.mapped('invoice_ids')
    #     action = self.env.ref('account.action_invoice_tree1').read()[0]
    #     if len(invoices) > 1:
    #         action['domain'] = [('id', 'in', invoices.ids)]
    #     elif len(invoices) == 1:
    #         action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
    #         action['res_id'] = invoices.ids[0]
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action