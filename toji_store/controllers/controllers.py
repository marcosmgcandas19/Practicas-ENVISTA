# -*- coding: utf-8 -*-
# from odoo import http


# class TojiStore(http.Controller):
#     @http.route('/toji_store/toji_store', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/toji_store/toji_store/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('toji_store.listing', {
#             'root': '/toji_store/toji_store',
#             'objects': http.request.env['toji_store.toji_store'].search([]),
#         })

#     @http.route('/toji_store/toji_store/objects/<model("toji_store.toji_store"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('toji_store.object', {
#             'object': obj
#         })

