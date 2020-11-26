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


class VehicleCreation(models.Model):
    _name = 'sale.vehicle'

    name = fields.Char(string="Nombre del vehiculo", required=True)
    #driver_name = fields.Many2one('res.partner', string="Nombre de contacto")
    driver_name = fields.Many2one('transport.transportista', string="Nombre de contacto")
    vehicle_image = fields.Binary(string='Imagen', store=True, attachment=True)
    licence_plate = fields.Char(string="Placa", required=True)
    mob_no = fields.Char(string="Número de teléfono movil")
    vehicle_address = fields.Char(string="Direccion")
    vehicle_city = fields.Char(string='Ciudad')
    vehicle_zip = fields.Char(string='CODIGO POSTAL')
    state_id = fields.Many2one('res.country.state', string='Estado')
    country_id = fields.Many2one('res.country', string='Pais')
    active_available = fields.Boolean(string="Activo", default=True)

class PuertoAreopuertoEmbarque(models.Model):
    _name = 'puerto.aeropuerto.embarque'

    name = fields.Char(string="Codigo", required=True)
    Descripcion = fields.Char(string="Descripcion", required=True)

class PuertoAreopuertoDesembarque(models.Model):
    _name = 'puerto.aeropuerto.desembarque'

    name = fields.Char(string="Codigo", required=True)
    Descripcion = fields.Char(string="Descripcion", required=True)