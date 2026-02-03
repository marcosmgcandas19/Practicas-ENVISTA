# -*- coding: utf-8 -*-
# from odoo import http


# class Cinevista(http.Controller):
#     @http.route('/cinevista/cinevista', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cinevista/cinevista/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cinevista.listing', {
#             'root': '/cinevista/cinevista',
#             'objects': http.request.env['cinevista.cinevista'].search([]),
#         })

#     @http.route('/cinevista/cinevista/objects/<model("cinevista.cinevista"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cinevista.object', {
#             'object': obj
#         })

