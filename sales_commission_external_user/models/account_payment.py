# -*- coding: utf-8 -*-
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
#from openerp import models, fields, api, _
#from openerp.exceptions import Warning
#from openerp.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import UserError


class AccountPayment(models.Model):

    _inherit = "account.payment"

    @api.model
    def _get_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.company_id.commission_based_on if self.company_id else self.env.company.commission_based_on
#         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#        when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.when_to_pay') #odoo11
        when_to_pay = self.company_id.when_to_pay if self.company_id else self.env.company.when_to_pay
        if commission_based_on == 'sales_team' and when_to_pay == 'invoice_payment':
            return True

    #@api.multi
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
#     sales_user_id = fields.Many2one(
#         'res.users',
#         string='Salesperson',
#     )
#     commission_manager_id = fields.Many2one(
#         'sales.commission.line',
#         string='Sales Commission for Manager'
#     )
#     commission_person_id = fields.Many2one(
#         'sales.commission.line',
#         string='Sales Commission for Member'
#     )
    sales_commission_apply = fields.Boolean(
        string='Sales Commission Apply',
        compute='_check_partner_type',
        store=True,
    )
    sale_commission_user_ids = fields.One2many(
        'sale.commission.level.users',
        'payment_id',
        string="Sale Commission User"
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'account_payment_id',
        string="Sale Commission Level Percentage"
    )
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )

    #@api.multi
    @api.depends()
    def _compute_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.company_id.commission_based_on if self.company_id else self.env.company.commission_based_on
#         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#        when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.when_to_pay') #odoo11
        when_to_pay = self.company_id.when_to_pay if self.company_id else self.env.company.when_to_pay
        for rec in self:
            rec.is_apply = False
            if commission_based_on == 'sales_team' and when_to_pay == 'invoice_payment':
                rec.is_apply = True

    #@api.multi
    @api.onchange('sales_team_id')
    def sales_team_id_change(self):
        for rec in self:
            sale_commission_percentage = [(5, 0)]
            for level in rec.sales_team_id.sale_commission_percentage_ids:
                sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                        'percentage': level.percentage,
                                        'account_payment_id':rec.id}))
#            exist_sale_commission_percentage_ids = rec.sale_commission_percentage_ids #12/09/2019
            rec.sale_commission_percentage_ids = sale_commission_percentage #12/09/2019
#            rec.sale_commission_percentage_ids -= exist_sale_commission_percentage_ids #12/09/2019
            # rec.sale_commission_percentage_ids = sale_commission_percentage

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
#        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if self._context.get('active_model') and self._context.get('active_model')  == 'account.move':
            invoice_defaults = self.env[self._context.get('active_model')].browse(self._context.get('active_ids', False))
            if invoice_defaults and len(invoice_defaults) == 1:
                invoice = invoice_defaults[0]
                rec['sales_team_id'] = invoice['team_id'].id and invoice['team_id'][0].id or False
        return rec

    #@api.multi
    @api.onchange('partner_id')
    def partner_id_change(self):
        for rec in self:
            if rec.partner_id:
                sale_commission = []
                for level in rec.partner_id.sale_commission_user_ids:
                    sale_commission.append((0, 0, {'level_id': level.level_id.id,
                                            'user_id': level.user_id.id,
                                            'payment_id':rec.id}))
                rec.sale_commission_user_ids = sale_commission

    #@api.multi
    def get_teamwise_commission(self):
        for rec in self:
            if not rec.sales_team_id:
                raise UserError(_('Please select Sales Team.'))
#             if not rec.sales_user_id:
#                 raise UserError(_('Please select Sales User.'))
            
            commission = {}
            for commission_id in rec.sale_commission_percentage_ids:
                for partner in rec.sale_commission_user_ids:
                    if partner.level_id == commission_id.level_id:
                        amount = (rec.amount * commission_id.percentage)/100
                        if partner.user_id not in commission:
                            commission[partner.user_id] = 0.0
                        commission[partner.user_id] += amount
        return commission

    #@api.multi
    def create_commission(self, user_commission,commission):
        commission_obj = self.env['sales.commission.line']
        product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
        for user in user_commission:
            for payment in self:
                if user_commission:
                    for sale_commission in commission.commission_user_id:
                        if user.id == sale_commission.id:
                            commission_value = {
                                'commission_user_id': user.id,
                                'amount': user_commission[user],
                                'origin': payment.name,
                                #'user_id': user.id,
                                'product_id': product.id,
#                                'date' : payment.payment_date,
                                'date' : payment.date,
                                'src_payment_id': payment.id,
                                'sales_commission_id':commission.id,
                                'sales_team_id': payment.sales_team_id.id,
                                'type': 'sales_person',
                                'company_id': payment.company_id.id,
                                'currency_id': payment.company_id.currency_id.id,
                            }
                            commission_id = commission_obj.sudo().create(commission_value)
#                            payment.commission_person_id = commission_id.id
        return True

    #@api.multi
    def create_base_commission(self, user):
        commission_obj = self.env['sales.commission']
        product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
        if user:
            for order in self:
#                today = date.today()
#                first_day = today.replace(day=1)
#                last_day = datetime.datetime(today.year,today.month,1)+relativedelta(months=1,days=-1)

                first_day_tz, last_day_tz = self.env['sales.commission']._get_utc_start_end_date()

                commission_value = {
#                        'start_date' : first_day,
#                        'end_date': last_day,
                        'start_date' : first_day_tz,
                        'end_date': last_day_tz,
                        'product_id':product.id,
                        'commission_user_id': user.id,
                        'company_id': order.company_id.id,
                    }
                commission_id = commission_obj.sudo().create(commission_value)
            return commission_id
    
    #@api.multi
#    def post(self):
#        res = super(AccountPayment, self).post()
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        if self.env.context.get('skip'): #odoo11 skip real_estate_property_app
            return res
#         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#        when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.when_to_pay') #odoo11
        when_to_pay = self.env.company.when_to_pay
        if  when_to_pay == 'invoice_payment':
            for payment in self:
                if payment.sales_commission_apply:
#                     commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#                    commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
                    commission_based_on = payment.company_id.commission_based_on
                    if commission_based_on == 'sales_team':
                        user_commission = payment.get_teamwise_commission()
                        for user in user_commission:
                            commission = self.env['sales.commission'].search([
                                ('commission_user_id', '=', user.id),
#                                ('start_date', '<', payment.payment_date),
#                                ('end_date', '>', payment.payment_date),
                                ('start_date', '<', payment.date),
                                ('end_date', '>', payment.date),
                                ('state','=','draft'),
                                ('company_id', '=', payment.company_id.id),
                                ],limit=1)
                            if not commission:
                                commission = payment.create_base_commission(user)
                            if  commission:
                                payment.create_commission(user_commission, commission)
        return res

    #@api.multi
#    def cancel(self):
    def action_cancel(self):
        commission_obj = self.env['sales.commission.line']
#        res = super(AccountPayment, self).cancel()
        res = super(AccountPayment, self).action_cancel()
        for rec in self:
            lines = commission_obj.sudo().search([('src_payment_id', '=', rec.id)])
            for line in lines:
                if line.state == 'draft' or line.state == 'cancel':
                    line.state = 'exception'
                elif line.state in ('paid', 'invoice'):
                    raise UserError(_('You can not cancel this payment because sales commission is invoiced/paid already. Please cancel related commission lines firt and then try again.'))
            #if rec.commission_manager_id:
             #   rec.commission_manager_id.state = 'exception'
            #if rec.commission_person_id:
             #   rec.commission_person_id.state = 'exception'
        return res
