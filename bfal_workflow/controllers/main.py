
from odoo import http, _
from odoo.osv import expression
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request


class PortalAccount(CustomerPortal):

    @http.route(["/invoice/tip"], type="json", auth="public")
    def jitsi_is_full(self, tip_percent, tip_amount, inv_id, **kw):
        inv_id = request.env['account.move'].sudo().browse(int(inv_id))
        request.env['tip.assign.amount'].sudo().with_context(active_id=inv_id.id).create({
            'tip_amount': tip_percent,
            'tip_value': tip_amount,
        }).action_assign_tip()
        inv_id.action_post()