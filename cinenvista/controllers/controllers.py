# -*- coding: utf-8 -*-
# from odoo import http


# class Cinenvista(http.Controller):
#     @http.route('/cinenvista/cinenvista', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cinenvista/cinenvista/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cinenvista.listing', {
#             'root': '/cinenvista/cinenvista',
#             'objects': http.request.env['cinenvista.cinenvista'].search([]),
#         })

#     @http.route('/cinenvista/cinenvista/objects/<model("cinenvista.cinenvista"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cinenvista.object', {
#             'object': obj
#         })

