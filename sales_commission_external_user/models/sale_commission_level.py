# -*- coding: utf-8 -*-

#from openerp import models, fields, api
from odoo import models, fields, api


class SaleOrder(models.Model):
    _name = "sale.commission.level"

    name = fields.Char(
        string="Commission Level",
        required=True,
    )
    commission_user_ids = fields.Many2one(
        'sale.commission.level.users',
        string="Product Template",
    )
    commission_percentage_ids = fields.Many2one(
        'sale.commission.level.percentage',
        string="Commission Percentage",
    )
