# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)

class SupportTeam(models.Model):

    _name = "support.team"   
    _inherit = ['mail.alias.mixin', 'mail.thread']
    _description = "Support Team"    
    
    name = fields.Char('Helpdesk Team', required=True, translate=True)    
    alias_id = fields.Many2one('mail.alias', string='Alias', required=True, help="The email address associated with this channel. New emails received will automatically create new leads assigned to the channel.")
    user_id = fields.Many2one('res.users',string="Responsible")
    parent_team_id = fields.Many2one('support.team',string="Parent Team")
    team_member = fields.Many2many('res.users','res_user_rel','support_team_id','user_id',string="Team Member")
    level = fields.Selection([('s_level_1','Level 1'),('s_level_2','Level 2'),('s_level_3','Level 3')])
    team_leader = fields.Many2one('res.users',string="Team Leader")

    def get_alias_values(self):
        values = super(SupportTeam, self).get_alias_values()
        
        values['alias_defaults'] = defaults = safe_eval(self.alias_defaults or "{}")
        defaults['support_team_id'] = self.id
        return values

    def get_alias_model_name(self, vals):
        return 'support.ticket'

    def write(self, vals):
        result = super(SupportTeam, self).write(vals)
        if 'alias_defaults' in vals:
            for team in self:
                team.alias_id.write(team.get_alias_values())
        return result
