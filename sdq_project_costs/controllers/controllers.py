# -*- coding: utf-8 -*-
from odoo import http

# class SdqProjectCosts(http.Controller):
#     @http.route('/sdq_project_costs/sdq_project_costs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sdq_project_costs/sdq_project_costs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sdq_project_costs.listing', {
#             'root': '/sdq_project_costs/sdq_project_costs',
#             'objects': http.request.env['sdq_project_costs.sdq_project_costs'].search([]),
#         })

#     @http.route('/sdq_project_costs/sdq_project_costs/objects/<model("sdq_project_costs.sdq_project_costs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sdq_project_costs.object', {
#             'object': obj
#         })