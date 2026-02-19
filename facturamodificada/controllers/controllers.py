# -*- coding: utf-8 -*-
# from odoo import http


# class Facturamodificada(http.Controller):
#     @http.route('/facturamodificada/facturamodificada', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/facturamodificada/facturamodificada/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('facturamodificada.listing', {
#             'root': '/facturamodificada/facturamodificada',
#             'objects': http.request.env['facturamodificada.facturamodificada'].search([]),
#         })

#     @http.route('/facturamodificada/facturamodificada/objects/<model("facturamodificada.facturamodificada"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('facturamodificada.object', {
#             'object': obj
#         })

