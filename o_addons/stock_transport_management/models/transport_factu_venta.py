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

from odoo import models, fields, api


class VehicleSaleOrder(models.Model):
    _inherit = 'stock.picking'

    transportista = fields.Many2one('transport.transportista', string="Conductor", required=True,default=lambda self: self.env['transport.transportista'].search([],limit=1))
    entreg_tercero = fields.Boolean(default=False,string="Entregar a Terceros")
    tercera_persona = fields.Many2one('res.partner', string="Tercero")
    puerto_embar=fields.Many2one('puerto.aeropuerto.embarque', string="Puerto/aeropuerto de embarque")
    puerto_desembar=fields.Many2one('puerto.aeropuerto.desembarque', string="Puerto/aeropuerto de desembarque")
    contenedor=fields.Many2one('transport.contenedor', string="Datos del Contenedor")
    transport_date = fields.Date(string="Fecha de inicio del traslado",default=lambda self: fields.Datetime.now(), required=True)#default=lambda self: self.min_date
    motivo_traslado=fields.Many2one('einvoice.catalog.20', string="Motivo del Traslado", required=True, default=lambda self: self.env['einvoice.catalog.20'].search([],limit=1))
    modalidad_traslado=fields.Many2one('einvoice.catalog.18', string="Modalidad del Traslado", required=True, default=lambda self: self.env['einvoice.catalog.18'].search([],limit=1))
    Indicador_de_transbordo=fields.Boolean(default=False, string="¿Transbordo programado?") 
    #peso_bruto = fields.Char(string="Peso bruto total de la GRE")
    #unidad_peso_bruto = fields.Many2one('einvoice.catalog.03', string="Unidad de medida del peso bruto total de la GRE")
    descripcion_motivo_traslado = fields.Char(default="-",string="Descripcion de motivo de Traslado")#Orden de entrega 
    required_condition=fields.Boolean(default=False, string="required condition") 
    
    @api.multi
    @api.onchange('motivo_traslado')
    def onchange_motivo_tras(self):
        for rec in self:
            if rec.motivo_traslado.code=='08':
                rec.required_condition = True
            else:
                rec.required_condition = False
    '''transportation_name = fields.Char(string="Transportation Via", compute="get_transportation")
    no_parcels = fields.Integer(string="No Of Parcels")
    transportation_details = fields.One2many('vehicle.status', compute='fetch_details', string="Transportation Details")
    
    
    @api.multi
    def get_transportation(self):
        res = self.env['sale.order'].search([('name', '=', self.sale_id.name)])
        self.transportation_name = res.transportation_name.name
        order = self.env['vehicle.status'].search([('sale_order', '=', self.sale_id.name)])
        if not order and self.transportation_name:
            vals = {'name': self.transportation_name,
                    'no_parcels': self.no_parcels,
                    'sale_order': self.sale_id.name,
                    'delivery_order': self.name,
                    'transport_date': self.min_date,
                    }
            obj = self.env['vehicle.status'].create(vals)
            return obj

    @api.onchange('no_parcels')
    def get_parcel(self):
        order = self.env['vehicle.status'].search([('sale_order', '=', self.sale_id.name)])
        vals = {'no_parcels': self.no_parcels}
        order.write(vals)

    @api.multi
    def fetch_details(self):
        order = self.env['vehicle.status'].search([('sale_order', '=', self.sale_id.name)])
        self.transportation_details = order
    '''

class Vehicleaccountinvoice(models.Model):
    _inherit = 'account.invoice'

    #transportation_name = fields.Char(string="Transporte via")
    #no_parcels = fields.Integer(string="No de Paquetes")
    #transporte = fields.Many2one('sale.vehicle', string="Vehiculo")
    #ubigeo_llegada=fields.Char(string="Ubigeo ")
    #ubigeo_llegada=fields.Many2one('einvoice.catalog.13',string="Ubigeo ")
    #direccion_llegada = fields.Char(string="Direccion")
    #ubigeo_partida=fields.Char(string="Ubigeo ")
    #ubigeo_partida=fields.Many2one('einvoice.catalog.13',string="Ubigeo ")
    #direccion_partida = fields.Char(string="Direccion")
    transportista = fields.Many2one('transport.transportista', string="Conductor")
    #conductor = fields.Many2one('transport.conductor', string="Conductor")
    entreg_tercero = fields.Boolean(default=False,string="Entregar a Terceros")
    tercera_persona = fields.Many2one('res.partner', string="Tercero")
    puerto_embar=fields.Many2one('puerto.aeropuerto.embarque', string="Puerto/aeropuerto de embarque")
    puerto_desembar=fields.Many2one('puerto.aeropuerto.desembarque', string="Puerto/aeropuerto de desembarque")
    contenedor=fields.Many2one('transport.contenedor', string="Datos del Contenedor")
    #datos_envio=fields.Many2one('vehicle.status', string="Datos de Envio") 
    transport_date = fields.Date(string="Fecha de inicio del transporte")
    motivo_traslado=fields.Many2one('einvoice.catalog.20', string="Motivo del Traslado")
    modalidad_traslado=fields.Many2one('einvoice.catalog.18', string="Modalidad del Traslado")
    #no_paquetes = fields.Char(string="Nro de paquetes") 
    Indicador_de_transbordo=fields.Boolean(default=False, string="Indicador del transbordo programado") 
    peso_bruto = fields.Char(string="Peso bruto total de la GRE")
    unidad_peso_bruto = fields.Many2one('einvoice.catalog.03', string="Unidad de medida del peso bruto total de la GRE")
    descripcion_motivo_traslado = fields.Char(string="Descripcion de motivo de Traslado")#Orden de entrega 

class DatosDelContenedor(models.Model):
    _name = 'transport.contenedor'

    name = fields.Char(string="Numero de Contenedor", required=True)
    Descripcion = fields.Char(string="Descripcion")