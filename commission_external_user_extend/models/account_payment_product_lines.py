# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
#from openerp.exceptions import Warning
from odoo import models, fields, api, _
#from odoo.exceptions import Warning


class AccountPaymentProductLines(models.Model):
    _name = 'account.payment.product.lines'

    @api.model
    def _get_is_apply(self):
        ConfigParameterObj = self.env['ir.config_parameter'].sudo()
        commission_based_on = ConfigParameterObj.get_param(
            'sales_commission_external_user.commission_based_on'
        )
        when_to_pay = ConfigParameterObj.get_param(
            'sales_commission_external_user.when_to_pay'
        )
        if commission_based_on != 'sales_team' and when_to_pay == 'invoice_payment':
            return True
        return False

    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required=True,
    )
    amount_total = fields.Float(
        string="Amount Total",
        required=True,
    )
    payment_id = fields.Many2one(
        'account.payment',
        string="Payment",
    )
    
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'payment_product_line_id',
        string="Sale Commission Level Percentage"
    )

    commission_percent_ids = fields.Many2many(
        'sale.commission.level.percentage',
        'commision_level_payment_line_rel',
        'payment_line_id',
        'percent_id',
        string="Commission Level Percentage",
    ) #odoo11

    #@api.multi
    @api.depends()
    def _compute_is_apply(self):
        for rec in self:
            rec.is_apply = rec._get_is_apply()

    #@api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        commission_based_on = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.commission_based_on'
        )
        for rec in self:
            rec.amount_total = rec.product_id.lst_price
            if commission_based_on:
                sale_commission_percentage = []
                if commission_based_on == 'product_category':
                    for level in rec.product_id.categ_id.sale_commission_percentage_ids:
                        sale_commission_percentage.append(level.id)
                elif commission_based_on == 'product_template':
                    for level in rec.product_id.sale_commission_percentage_ids:
                        sale_commission_percentage.append(level.id)
                rec.commission_percent_ids = [(6, 0,sale_commission_percentage)]
