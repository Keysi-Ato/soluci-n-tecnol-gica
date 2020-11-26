# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Saritha Sahadevan(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (AGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class VehicleStatus(models.Model):
    _name = 'vehicle.status'

    name = fields.Char(string="Identificador", required=True)
    transport_date = fields.Date(string="Fecha de inicio del transporte")
    #motivo_traslado=fields.Many2one('motivos.traslados', string="Motivo del Traslado")
    motivo_traslado=fields.Many2one('einvoice.catalog.20', string="Motivo del Traslado")
    #modalidad_traslado=fields.Many2one('modalidad.traslados', string="Modalidad del Traslado")
    modalidad_traslado=fields.Many2one('einvoice.catalog.18', string="Modalidad del Traslado")
    no_parcels = fields.Char(string="Nro de paquetes")
    peso_bruto = fields.Char(string="Peso bruto total de la GRE")
    #unidad_peso_bruto = fields.Char(string="Unidad de medida del peso bruto total de la GRE")
    unidad_peso_bruto = fields.Many2one('einvoice.catalog.03', string="Unidad de medida del peso bruto total de la GRE")
    #sale_order = fields.Char(string='Pedir Referencia')
    delivery_order = fields.Char(string="Descripcion de motivo de Traslado")#Orden de entrega 
    state = fields.Selection([
        ('draft', 'Draft'),
        ('start', 'Start'),
        ('waiting', 'Waiting'),
        ('cancel', 'Cancel'),
        ('done', 'Done'),
    ], string='Estado', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    def start_action(self):
        vehicle = self.env['sale.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': False}
        vehicle.write(vals)
        self.write({'state': 'start'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
        vehicle = self.env['sale.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': True}
        vehicle.write(vals)

    def action_done(self):
        self.write({'state': 'done'})
        vehicle = self.env['sale.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': True}
        vehicle.write(vals)

    def action_waiting(self):
        vehicle = self.env['sale.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': False}
        vehicle.write(vals)
        self.write({'state': 'waiting'})

    def action_reshedule(self):
        self.write({'state': 'draft'})


class MotivosTraslado(models.Model):
    _name = 'motivos.traslados'

    name = fields.Char(string="Codigo", required=True)
    descripcion = fields.Char(string="Descripcion", required=True)
    
class MotivosTraslado(models.Model):
    _name = 'modalidad.traslados'

    name = fields.Char(string="Codigo", required=True)#
    descripcion = fields.Char(string="Descripcion", required=True)
