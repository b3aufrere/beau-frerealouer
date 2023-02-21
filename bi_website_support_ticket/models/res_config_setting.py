# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    support_ticket_visible = fields.Selection([
        ('public_user_ticket', 'Support Ticket For All Public User'),
        ('login_user_ticket', 'Support Ticket For Login User'),
    ], string='Support Ticket',default='public_user_ticket')

    support_team_id = fields.Many2one('support.team', string = "Default Support Team")
    
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        team_id = self.env['ir.config_parameter'].sudo().get_param('bi_website_support_ticket.support_team_id')
        res.update(
            support_ticket_visible = self.env['ir.config_parameter'].sudo().get_param('bi_website_support_ticket.support_ticket_visible'),
            support_team_id = int(team_id) or False,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('bi_website_support_ticket.support_ticket_visible', self.support_ticket_visible)
        self.env['ir.config_parameter'].sudo().set_param('bi_website_support_ticket.support_team_id', self.support_team_id.id)
        