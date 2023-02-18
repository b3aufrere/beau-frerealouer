# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)

class support_ticket_stage(models.Model):
    _name = "support.ticket.stage"
    _rec_name = 'name'
    _order = "sequence"
    _description = "Support Ticket Stage"


    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.",default=lambda *args: 1)
    team_ids = fields.Many2many('support.team', 'crm_team_claim_stage_rel', 'stage_id', 'team_id', string='Teams')
    case_default = fields.Boolean('Common to All Teams')

    _defaults = {
        'sequence': lambda *args: 1
    }  