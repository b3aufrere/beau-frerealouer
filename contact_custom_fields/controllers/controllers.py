# -*- coding: utf-8 -*-
# from odoo import http


# class ContactCustomFields(http.Controller):
#     @http.route('/contact_custom_fields/contact_custom_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contact_custom_fields/contact_custom_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contact_custom_fields.listing', {
#             'root': '/contact_custom_fields/contact_custom_fields',
#             'objects': http.request.env['contact_custom_fields.contact_custom_fields'].search([]),
#         })

#     @http.route('/contact_custom_fields/contact_custom_fields/objects/<model("contact_custom_fields.contact_custom_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contact_custom_fields.object', {
#             'object': obj
#         })
