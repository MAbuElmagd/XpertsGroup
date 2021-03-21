# -*- coding: utf-8 -*-
from odoo import http

# class XpertsEmployee(http.Controller):
#     @http.route('/xperts_employee/xperts_employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/xperts_employee/xperts_employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('xperts_employee.listing', {
#             'root': '/xperts_employee/xperts_employee',
#             'objects': http.request.env['xperts_employee.xperts_employee'].search([]),
#         })

#     @http.route('/xperts_employee/xperts_employee/objects/<model("xperts_employee.xperts_employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('xperts_employee.object', {
#             'object': obj
#         })