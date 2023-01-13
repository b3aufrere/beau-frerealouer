# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class TwilioSmsGroups(models.Model):
    _name = 'twilio.sms.groups'
    _description = "Twilio SMS Groups"
    
    @api.depends('recipients')
    def _compute_total_recipients(self):
        for sms_group_id in self:
            sms_group_id.recipients_count = len(sms_group_id.recipients)
    
    name = fields.Char("Group Name", help="Group name", required=True, copy=False)
    active = fields.Boolean("Active", default=True)
    recipients_count = fields.Integer(string='recipients Count', compute='_compute_total_recipients')
    recipients = fields.Many2many("res.partner", 'twilio_sms_groups_res_partner_rel', 'sms_group_id', 'partner_id',
                                    "Recipients", required=True)
    
    # Odoo Logic Section
    # =====================
    def action_view_recipients(self):
        """
            :return: action or error
        """
        recipients = self.env['res.partner'].sudo().search([('id', 'in', self.recipients.ids)])
        action = {
            'domain': "[('id', 'in', " + str(recipients.ids) + " )]",
            'name': "Recipients",
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
        }
        return action
    
    
    