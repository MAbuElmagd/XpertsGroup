# -*- coding: utf-8 -*-
# from odoo import http


# class Faq(http.Controller):
#     @http.route('/faq/faq/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/faq/faq/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('faq.listing', {
#             'root': '/faq/faq',
#             'objects': http.request.env['faq.faq'].search([]),
#         })

#     @http.route('/faq/faq/objects/<model("faq.faq"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('faq.object', {
#             'object': obj
#         })
