# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)

class SupportStage(models.Model):

    _name = "support.stage"
    _description = "Support Stage"
    
    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.",default=lambda *args: 1)
    fold = fields.Boolean(string="Folded in Form")

    _defaults = {
        'sequence': lambda *args: 1
    }       