# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
#from openerp.exceptions import Warning
from odoo import models, fields, api, _
#from odoo.exceptions import Warning


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def _get_is_apply(self):
        super(AccountPayment, self)._get_is_apply()
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
        print ("************",when_to_pay,commission_based_on)
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
        print ("********team")
        if when_to_pay == 'invoice_payment' and commission_based_on not in [
                                                'product_category', 'product_template']:
            return True
        return False

    #@api.multi
#    def _compute_is_team_commission(self):
#        for rec in self:
#            rec.is_team_commission = rec._get_team_commission()
            
    #@api.multi
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
        'account.payment.product.lines',
        'payment_id',
        string="Product Lines",
    )
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )


    #@api.multi
    @api.depends()
    def _compute_is_apply(self):
        super(AccountPayment, self)._compute_is_apply()
        when_to_pay = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.when_to_pay'
        )
        for rec in self:
            if when_to_pay == 'invoice_payment':
                rec.is_apply = True

    @api.model
    def get_categorywise_commission(self):
        for rec in self:
            commission = {}
            for line in rec.commission_product_line_ids:
                for commission_id in line.commission_percent_ids:
                    for partner in rec.sale_commission_user_ids:
                        if partner.level_id == commission_id.level_id:
                            amount = (line.amount_total * commission_id.percentage)/100
                            if partner.user_id not in commission:
                                commission[partner.user_id] = 0.0
                            commission[partner.user_id] += amount
        return commission

    #@api.multi
    def get_productwise_commission(self):
        for rec in self:
            commission = {}
            for line in rec.commission_product_line_ids:
                for commission_id in line.commission_percent_ids:
                    for partner in rec.sale_commission_user_ids:
                        if partner.level_id == commission_id.level_id:
                            amount = (line.amount_total * commission_id.percentage)/100
                            if partner.user_id not in commission:
                                commission[partner.user_id] = 0.0
                            commission[partner.user_id] += amount
        return commission

    #@api.multi
#    def post(self):
#        res = super(AccountPayment, self).post()
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        if self.env.context.get('skip'): 
            return res
        when_to_pay = self.env['ir.config_parameter'].sudo().get_param(
            'sales_commission_external_user.when_to_pay'
        )
        if  when_to_pay == 'invoice_payment':
            for payment in self:
                if payment.sales_commission_apply:
                    user_commission = False

                    commission_based_on = self.env['ir.config_parameter'].sudo().get_param(
                        'sales_commission_external_user.commission_based_on')
                    if commission_based_on == 'product_category':
                        user_commission = payment.get_categorywise_commission()
                    elif commission_based_on == 'product_template':
                        user_commission = payment.get_productwise_commission()

                    if user_commission:
                        for user in user_commission:
                            commission = self.env['sales.commission'].search([
                                ('commission_user_id', '=', user.id),
#                                ('start_date', '<', payment.payment_date),
#                                ('end_date', '>', payment.payment_date),
                                ('start_date', '<', payment.date),
                                ('end_date', '>', payment.date),
                                ('state','=','draft')],limit=1)
                            if not commission:
                                commission = payment.create_base_commission(user)
                            if  commission:
                                payment.create_commission(user_commission, commission)
        return res
