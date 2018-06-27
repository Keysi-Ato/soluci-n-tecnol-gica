
from odoo import fields, models, api
import os
# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     @api.multi
#     def action_view_invoice(self):
#         invoices = self.mapped('invoice_ids')
#         action = self.env.ref('account.action_invoice_tree1').read()[0]
#         action["context"]={
#                     'type':'out_invoice',
#                     'journal_type': 'sale',
#                     'type_code':'01',
#                 }
#         if len(invoices) > 1:
#             action['domain'] = [('id', 'in', invoices.ids)]
#         elif len(invoices) == 1:
#             action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
#             action['res_id'] = invoices.ids[0]
#         else:
#             action = {'type': 'ir.actions.act_window_close'}
#         return action


class SaleOrder(models.Model):
    _inherit = "sale.order"
    tipo_documento=fields.Selection(string="Tipo de Documento",selection=[('01','Factura'),('03','Boleta')], required=True)

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]

        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
            default_journal_id=self.env["account.journal"].search([["invoice_type_code_id", "=", self.tipo_documento]])
            action["context"]="{'type_code':'"+self.tipo_documento+"'}"
            if len(default_journal_id)>0:
                action["default_journal_id"] = default_journal_id[0].id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
