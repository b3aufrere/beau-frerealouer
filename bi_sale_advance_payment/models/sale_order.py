# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    account_payment_ids = fields.One2many('account.payment', 'sale_id', string="Pay Sale advanced", readonly=True)
