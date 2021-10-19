# -*- coding: utf-8 -*-
# from odoo import http


# class SsiPacking(http.Controller):
#     @http.route('/ssi_packing/ssi_packing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ssi_packing/ssi_packing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ssi_packing.listing', {
#             'root': '/ssi_packing/ssi_packing',
#             'objects': http.request.env['ssi_packing.ssi_packing'].search([]),
#         })

#     @http.route('/ssi_packing/ssi_packing/objects/<model("ssi_packing.ssi_packing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ssi_packing.object', {
#             'object': obj
#         })
