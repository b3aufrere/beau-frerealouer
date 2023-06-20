# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)


class SupportInvoice(models.Model):
    _name = 'support.invoice'
    _description = "Support Invoice" 
    
    support_invoice_id = fields.Many2one('support.ticket',string="Support Ticket Invoice")
    name = fields.Text(string='Description', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',ondelete='set null', index=True)
    price_unit = fields.Float(string='Unit Price', required=True)
    quantity = fields.Float(string='Quantity',required=True, default=1)
    invoice_line_tax_ids = fields.Many2many('account.tax',string="Taxes")