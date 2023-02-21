# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request

class SetBranch(http.Controller):

    @http.route('/set_brnach', type='json', auth="public", methods=['POST'], website=True)
    def custom_hours(self, BranchID, **post):
        print("\n\n\n\n==>> BranchID: ", BranchID)
        user_id = request.env['res.users'].sudo().search([('id','=',request.env.user.id)])
        print("==>> user_id: ", user_id)
        user_id.branch_id = BranchID[0]
        print("==>> user_id.branch_id: ", user_id.branch_id)
        return