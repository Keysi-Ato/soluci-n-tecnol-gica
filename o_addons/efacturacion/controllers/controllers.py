# -*- coding: utf-8 -*-
from odoo import http

# class Efacturacion(http.Controller):
#     @http.route('/efacturacion/efacturacion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/efacturacion/efacturacion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('efacturacion.listing', {
#             'root': '/efacturacion/efacturacion',
#             'objects': http.request.env['efacturacion.efacturacion'].search([]),
#         })

#     @http.route('/efacturacion/efacturacion/objects/<model("efacturacion.efacturacion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('efacturacion.object', {
#             'object': obj
#         })

