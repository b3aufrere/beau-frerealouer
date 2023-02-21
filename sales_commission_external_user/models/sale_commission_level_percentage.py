# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleCommissionPercentage(models.Model):
    _name = "sale.commission.level.percentage"

    level_id = fields.Many2one(
        'sale.commission.level',
        string="Commission Level",
        required=True,
    )
    percentage = fields.Float(
        string='Percentage (%)',
        required=True,
    )
    product_id = fields.Many2one(
        'product.template',
        string="Product Template",
    )
    product_category_id = fields.Many2one(
        'product.category',
        string="Product Category",
    )
    team_id = fields.Many2one(
        'crm.team',
        string="Sales Team",
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )
    sale_order_line_id =  fields.Many2one(
        'sale.order.line',
        string="Sale Order Line"
    )
#    account_id = fields.Many2one(
#        'account.invoice',
#        string="Account Invoice"
#    )
    account_id = fields.Many2one(
        'account.move',
        string="Account Invoice"
    )
#    account_invoice_line_id = fields.Many2one(
#        'account.invoice.line',
#        string="Account Invoice"
#    )
    account_invoice_line_id = fields.Many2one(
        'account.move.line',
        string="Account Invoice"
    )
    account_payment_id = fields.Many2one(
        'account.payment',
        string="Account Payment"
    )

    @api.model
    def create(self, vals):
        return super(SaleCommissionPercentage, self.sudo()).create(vals)

    @api.constrains('percentage')
    def _percentage_validation(self):
        for percentage in self:
            if percentage.percentage:
                if percentage.percentage < 0.0 or percentage.percentage > 100.0:
                    raise ValidationError(_('Percentage must be between 0.0 to 100.0!'))

    @api.constrains('level_id')
    def _level_validation(self):
        for level in self:
            domain = [('level_id', '=', level.level_id.id)]
            if level.sale_order_line_id:
                domain.append(('sale_order_line_id','=',level.sale_order_line_id.id))
            elif level.account_invoice_line_id:
                domain.append(('account_invoice_line_id','=',level.account_invoice_line_id.id))
            elif level.account_payment_id:
                domain.append(('account_payment_id','=',level.account_payment_id.id))
            elif level.team_id:
                domain.append(('team_id','=',level.team_id.id))
            elif level.sale_order_id:
                domain.append(('sale_order_id','=',level.sale_order_id.id))
            elif level.account_id:
                domain.append(('account_id','=',level.account_id.id))
            elif level.product_category_id:
                domain.append(('product_category_id','=',level.product_category_id.id))
            elif level.product_id:
                domain.append(('product_id','=',level.product_id.id))

            level_ids = self.search_count(domain)
            if level_ids > 1:
                raise ValidationError(_('Commission Levels must be unique!'))
