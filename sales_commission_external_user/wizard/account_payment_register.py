# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    @api.model
    def _get_is_apply(self):
        commission_based_on = self.company_id.commission_based_on if self.company_id else self.env.company.commission_based_on
        when_to_pay = self.company_id.when_to_pay if self.company_id else self.env.company.when_to_pay
        if commission_based_on == 'sales_team' and when_to_pay == 'invoice_payment':
            return True

    @api.depends('partner_type')
    def _check_partner_type(self):
        for rec in self:
            rec.sales_commission_apply = False
            if rec.partner_type == 'customer':
                rec.sales_commission_apply = True
        
    sales_team_id = fields.Many2one(
        'crm.team',
        string='Sales Team',
        required=False,
    )
    sales_commission_apply = fields.Boolean(
        string='Sales Commission Apply',
        compute='_check_partner_type',
        store=True,
    )
    sale_commission_user_ids = fields.One2many(
        'sale.commission.level.users.wiz',
        'payment_reg_id',
        string="Sale Commission User"
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage.wiz',
        'payment_reg_id',
        string="Sale Commission Level Percentage"
    )
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )

    @api.depends()
    def _compute_is_apply(self):
        commission_based_on = self.company_id.commission_based_on if self.company_id else self.env.company.commission_based_on
        when_to_pay = self.company_id.when_to_pay if self.company_id else self.env.company.when_to_pay
        for rec in self:
            rec.is_apply = False
            if commission_based_on == 'sales_team' and when_to_pay == 'invoice_payment':
                rec.is_apply = True

    @api.onchange('sales_team_id')
    def sales_team_id_change(self):
        for rec in self:
            sale_commission_percentage = [(5, 0)]
            for level in rec.sales_team_id.sale_commission_percentage_ids:
                sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                        'percentage': level.percentage,
                                        'payment_reg_id':rec.id}))
            rec.sale_commission_percentage_ids = sale_commission_percentage #12/09/2019

    @api.model
    def default_get(self, fields):
        rec = super(AccountPaymentRegister, self).default_get(fields)
        if self._context.get('active_model') and self._context.get('active_model')  == 'account.move':
            invoice_defaults = self.env[self._context.get('active_model')].browse(self._context.get('active_ids', False))
            if invoice_defaults and len(invoice_defaults) == 1:
                invoice = invoice_defaults[0]
                rec['sales_team_id'] = invoice['team_id'] and invoice['team_id'][0] or False
        return rec

    @api.onchange('partner_id')
    def partner_id_change(self):
        for rec in self:
            if rec.partner_id:
                sale_commission = []
                for level in rec.partner_id.sale_commission_user_ids:
                    sale_commission.append((0, 0, {'level_id': level.level_id.id,
                                            'user_id': level.user_id.id,
                                            'payment_reg_id':rec.id}))
                rec.sale_commission_user_ids = sale_commission
    
    
    # def _create_payment_vals_from_wizard(self):
    def _create_payment_vals_from_wizard(self, batch_result):
        # res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)

        if self.sale_commission_user_ids:
            sale_commission = []
            for level in self.sale_commission_user_ids:
                sale_commission.append((0, 0, {'level_id': level.level_id.id,
                                        'user_id': level.user_id.id}))
            res.update({
                'sale_commission_user_ids': sale_commission,
            })

        if self.sale_commission_percentage_ids:
            sale_commission_percentage = [(5, 0)]
            for level in self.sale_commission_percentage_ids:
                sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                        'percentage': level.percentage}))
            res.update({
                'sale_commission_percentage_ids': sale_commission_percentage,
            })
        return res
    
    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(batch_result)
        if self.sale_commission_user_ids:
            sale_commission = []
            for level in self.sale_commission_user_ids:
                sale_commission.append((0, 0, {'level_id': level.level_id.id,
                                        'user_id': level.user_id.id}))
            res.update({
                'sale_commission_user_ids': sale_commission,
            })

        if self.sale_commission_percentage_ids:
            sale_commission_percentage = [(5, 0)]
            for level in self.sale_commission_percentage_ids:
                sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                        'percentage': level.percentage}))
            res.update({
                'sale_commission_percentage_ids': sale_commission_percentage,
            })
        return res
