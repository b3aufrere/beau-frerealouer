# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentProductLines(models.TransientModel):
    _name = 'account.payment.product.lines.wiz'

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
    payment_reg_id = fields.Many2one(
        'account.payment.register',
        string="Payment",
    )
    
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )

    @api.depends()
    def _compute_is_apply(self):
        for rec in self:
            rec.is_apply = rec._get_is_apply()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        commission_based_on = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.commission_based_on'
        )
        for rec in self:
            rec.amount_total = rec.product_id.lst_price
