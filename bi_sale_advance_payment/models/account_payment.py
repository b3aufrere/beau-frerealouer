# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sale_id = fields.Many2one('sale.order', string="Sale", readonly=True)
