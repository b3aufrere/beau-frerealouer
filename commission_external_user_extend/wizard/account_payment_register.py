# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'


    @api.model
    def _get_is_apply(self):
        super(AccountPaymentRegister, self)._get_is_apply()
        when_to_pay = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.when_to_pay'
        )
        if when_to_pay == 'invoice_payment':
            return True

    @api.model
    def _get_product_commission(self):
        when_to_pay = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.when_to_pay'
        )
        commission_based_on = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.commission_based_on'
        )
        if when_to_pay == 'invoice_payment' and commission_based_on in [
                                                'product_category', 'product_template']:
            return True
        return False
    
    @api.model
    def _get_team_commission(self):
        when_to_pay = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.when_to_pay'
        )
        commission_based_on = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.commission_based_on'
        )
        if when_to_pay == 'invoice_payment' and commission_based_on not in [
                                                'product_category', 'product_template']:
            return True
        return False

    def _compute_is_product_commission(self):
        for rec in self:
            rec.is_product_commission = rec._get_product_commission()
            rec.is_team_commission = rec._get_team_commission()#13

    is_product_commission = fields.Boolean(
        string="Commission Based On Product",
        compute="_compute_is_product_commission",
        default=_get_product_commission
    )
    is_team_commission = fields.Boolean(
        string="Commission Based On Team",
        compute="_compute_is_product_commission",
        default=_get_team_commission
    )
    commission_product_line_ids = fields.One2many(
        'account.payment.product.lines.wiz',
        'payment_reg_id',
        string="Product Lines",
    )
    
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )

    @api.depends()
    def _compute_is_apply(self):
        super(AccountPaymentRegister, self)._compute_is_apply()
        when_to_pay = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.when_to_pay'
        )
        for rec in self:
            if when_to_pay == 'invoice_payment':
                rec.is_apply = True

    def _get_commission_perc(self, product_line):
        commission_based_on = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.commission_based_on'
        )
        percent_ids = []
        if commission_based_on:
            if commission_based_on == 'product_category':
                percent_ids = product_line.product_id.categ_id.sale_commission_percentage_ids.ids
            elif commission_based_on == 'product_template':
                percent_ids = product_line.product_id.sale_commission_percentage_ids.ids
        return percent_ids

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)

        if self.commission_product_line_ids:
            comm_product_line_ids = []
            for product_line in self.commission_product_line_ids:
                comm_product_line_ids.append((0, 0, {'product_id': product_line.product_id.id,
                                        'amount_total': product_line.amount_total,
                                        'commission_percent_ids': [(6, 0, self._get_commission_perc(product_line))]}))
            res.update({
                'commission_product_line_ids': comm_product_line_ids,
            })

        return res
    
    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(batch_result)
        if self.commission_product_line_ids:
            comm_product_line_ids = []
            for product_line in self.commission_product_line_ids:
                comm_product_line_ids.append((0, 0, {'product_id': product_line.product_id.id,
                                        'amount_total': product_line.amount_total,
                                        'commission_percent_ids': [(6, 0, self._get_commission_perc(product_line))]}))
            res.update({
                'commission_product_line_ids': comm_product_line_ids,
            })
        return res
