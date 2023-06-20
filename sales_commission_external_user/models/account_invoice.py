# -*- coding: utf-8 -*-
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
#from openerp import models, fields, api
from odoo import models, fields, api
#from openerp.exceptions import UserError, ValidationError
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
#    _inherit = "account.invoice"
    _inherit = "account.move"

    @api.model
    def _get_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.company_id.commission_based_on if self.company_id else self.env.company.commission_based_on
        if commission_based_on == 'sales_team':
            return True

    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )
    sale_commission_id = fields.Many2one(
        'sales.commission',
        string='Sales Commission',
        states={'draft': [('readonly', False)]}
    )
#     commission_manager_id = fields.Many2one(
#         'sales.commission.line',
#         string='Sales Commission for Manager'
#     )
#     commission_person_id = fields.Many2one(
#         'sales.commission.line',
#         string='Sales Commission for Member'
#     )
    sale_commission_user_ids = fields.One2many(
        'sale.commission.level.users',
        'account_id',
        string="Sale Commission User"
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'account_id',
        string="Sale Commission Level Percentage"
    )

    #@api.multi
    @api.depends()
    def _compute_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        for rec in self:
            commission_based_on = rec.company_id.commission_based_on if rec.company_id else self.env.company.commission_based_on
            rec.is_apply = False
            if commission_based_on == 'sales_team':
                rec.is_apply = True

    #@api.multi
    @api.onchange('partner_id')
    def partner_id_change(self):
        for rec in self:
            sale_commission = []
            for level in rec.partner_id.sale_commission_user_ids:
                sale_commission.append((0,0,{'level_id': level.level_id.id,
                                        'user_id': level.user_id.id,
                                        'order_id':rec.id}))
            rec.sale_commission_user_ids = sale_commission

    #@api.multi
    @api.onchange('team_id')
    def team_id_change(self):
        for rec in self:
            sale_commission_percentage = [(5, 0)]
            for level in rec.team_id.sale_commission_percentage_ids:
                sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                        'percentage': level.percentage,
                                        'sale_order_id':rec.id}))
            # rec.sale_commission_percentage_ids = sale_commission_percentage
#            exist_sale_commission_percentage_ids = rec.sale_commission_percentage_ids #12/09/2019
            rec.sale_commission_percentage_ids = sale_commission_percentage #12/09/2019
#            rec.sale_commission_percentage_ids -= exist_sale_commission_percentage_ids #12/09/2019

    @api.model
    def get_categorywise_commission(self):
        commission = {}
        for rec in self:
            for line in rec.invoice_line_ids:
#                 for commission_id in line.sale_commission_percentage_ids:
                for commission_id in line.commission_percentage_ids: #odoo11
                    for partner in rec.sale_commission_user_ids:
                        if partner.level_id == commission_id.level_id:
                            amount = (line.price_subtotal * commission_id.percentage)/100
                            if partner.user_id not in commission:
                                commission[partner.user_id] = 0.0
                            commission[partner.user_id] += amount
        return commission

    #@api.multi
    def get_productwise_commission(self):
        for rec in self:
            commission = {}
            for line in rec.invoice_line_ids:
#                 for commission_id in line.sale_commission_percentage_ids:
                for commission_id in line.commission_percentage_ids: #odoo11
                    for partner in rec.sale_commission_user_ids:
                        if partner.level_id == commission_id.level_id:
                            amount = (line.price_subtotal * commission_id.percentage)/100
                            if partner.user_id not in commission:
                                commission[partner.user_id] = 0.0
                            commission[partner.user_id] += amount
        return commission
    
    #@api.multi
    def get_teamwise_commission(self):
        commission = {}
        for rec in self:
            commission = {}
            for commission_id in rec.sale_commission_percentage_ids:
                for partner in rec.sale_commission_user_ids:
                    if partner.level_id == commission_id.level_id:
                        amount = (rec.amount_untaxed * commission_id.percentage)/100
                        if partner.user_id not in commission:
                            commission[partner.user_id] = 0.0
                        commission[partner.user_id] += amount
        return commission

    #@api.multi
    def create_commission(self, user_commission,commission):
        commission_obj = self.env['sales.commission.line']
        product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
        for user in user_commission:
            for invoice in self:
#                date_invoice = invoice.date_invoice
                date_invoice = invoice.invoice_date
                if not date_invoice:
                    date_invoice = fields.Date.context_today(self)
                origin = ''
#                if invoice.number:
#                    origin = invoice.number    
                if invoice.name:
#                    origin = origin + '-' +  invoice.name
                    origin = invoice.name
#                if invoice.origin:
                if invoice.invoice_origin:
#                    origin = origin + '-' +  invoice.origin
                    origin = origin + '-' +  invoice.invoice_origin
                if user_commission:
                    for sale_commission in commission.commission_user_id:
                        if user.id == sale_commission.id:
                            commission_value = {
                                #'sales_membar_user_id': user.id,
                                'amount': user_commission[user],
                                'origin': origin,
                                'commission_user_id': user.id,
                                'product_id': product.id,
                                'date' : date_invoice,
                                'src_invoice_id': invoice.id,
                                'sales_commission_id':commission.id,
                                'sales_team_id': invoice.team_id and invoice.team_id.id or False,
                                'type': 'sales_person',
                                'company_id': invoice.company_id.id,
                                'currency_id': invoice.company_id.currency_id.id,
                            }
                            commission_id = commission_obj.sudo().create(commission_value)
#                            invoice.commission_person_id = commission_id.id
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
                        'currency_id': order.currency_id.id,
                    }
                commission_id = commission_obj.sudo().create(commission_value)
            return commission_id
    
    #@api.multi
#    def invoice_validate(self):
    def action_post(self):
#        res = super(AccountInvoice, self).invoice_validate()
        res = super(AccountInvoice, self).action_post()
#         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#        when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.when_to_pay') #odoo11
        when_to_pay = self.env.company.when_to_pay
        if  when_to_pay == 'invoice_validate':
#             commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#            commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
#            if commission_based_on == 'sales_team':
#                user_commission = self.get_teamwise_commission()
#            elif commission_based_on == 'product_category':
#                user_commission = self.get_categorywise_commission()
#            elif commission_based_on == 'product_template':
#                user_commission = self.get_productwise_commission()
            for invoice in self:
                commission_based_on = invoice.company_id.commission_based_on
                if commission_based_on == 'sales_team':
                    user_commission = self.get_teamwise_commission()
                elif commission_based_on == 'product_category':
                    user_commission = self.get_categorywise_commission()
                elif commission_based_on == 'product_template':
                    user_commission = self.get_productwise_commission()
#                date_invoice = invoice.date_invoice
                date_invoice = invoice.invoice_date
                if not date_invoice:
                    date_invoice = fields.Date.context_today(self)
                for user in user_commission:
                    commission = self.env['sales.commission'].search([
                        ('commission_user_id', '=', user.id),
                        ('start_date', '<', date_invoice),
                        ('end_date', '>', date_invoice),
                        ('state','=','draft'),
                        ('company_id', '=', invoice.company_id.id),
                        ],limit=1)
                    if not commission:
                        commission = invoice.create_base_commission(user)
                    if  commission:
                        invoice.create_commission(user_commission, commission)
        return res
    
    #@api.multi
#    def action_invoice_cancel(self):
    def button_cancel(self):
#        res = super(AccountInvoice, self).action_invoice_cancel()
        res = super(AccountInvoice, self).button_cancel()
        commission_obj = self.env['sales.commission.line']
        for rec in self:
            lines = commission_obj.sudo().search([('src_invoice_id', '=', rec.id)])
            for line in lines:
                if line.state == 'draft' or line.state == 'cancel':
                    line.state = 'exception'
                elif line.state in ('paid', 'invoice'):
                    raise UserError(_('You can not cancel this invoice because sales commission is invoiced/paid. Please cancel related commission lines and try again.'))
            #if rec.commission_manager_id:
            #    rec.commission_manager_id.state = 'exception'
            #if rec.commission_person_id:
            #    rec.commission_person_id.state = 'exception'
        return res

class AccountInvoiceLine(models.Model):
#    _inherit = "account.invoice.line"
    _inherit = "account.move.line"

    @api.model
    def _get_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.company_id.commission_based_on if self.company_id else self.env.company.commission_based_on
#         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#        when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.when_to_pay') #odoo11
        when_to_pay = self.company_id.when_to_pay if self.company_id else self.env.company.when_to_pay
        if commission_based_on != 'sales_team' and when_to_pay == 'invoice_validate':
            return True

    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'account_invoice_line_id',
        string="Sale Commission Level Percentage"
    )

    commission_percentage_ids = fields.Many2many(
        'sale.commission.level.percentage',
        string="Commission Level Percentage",
    ) #odoo11

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
            if commission_based_on != 'sales_team' and when_to_pay == 'invoice_validate':
                rec.is_apply = True

#    #@api.multi
#    @api.onchange('product_id')
#    def _onchange_product_id(self):
#        res = super(AccountInvoiceLine, self)._onchange_product_id()
##         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
#        for rec in self:
#            if commission_based_on:
#                sale_commission_percentage = []
#                if commission_based_on == 'product_category':
#                    for level in rec.product_id.categ_id.sale_commission_percentage_ids:
##                        sale_commission_percentage.append(level.id)
#                        sale_commission_percentage = rec.product_id.categ_id.sale_commission_percentage_ids
#                elif commission_based_on == 'product_template':
#                    for level in rec.product_id.sale_commission_percentage_ids:
#                        sale_commission_percentage.append(level.id)
#                rec.commission_percentage_ids = sale_commission_percentage
##                 if commission_based_on == 'product_category':
##                     for level in rec.product_id.categ_id.sale_commission_percentage_ids:
##                         sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
##                                                 'percentage': level.percentage,
##                                                 'account_invoice_line_id':rec.id}))
##                 elif commission_based_on == 'product_template':
##                     for level in rec.product_id.sale_commission_percentage_ids:
##                         sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
##                                                 'percentage': level.percentage,
##                                                 'account_invoice_line_id':rec.id}))
##                 rec.sale_commission_percentage_ids = sale_commission_percentage
#        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('product_id'):
#                commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on')
                company_id = self.env['res.company'].browse(vals.get("company_id")) if vals.get("company_id") else False
                commission_based_on = company_id.commission_based_on if company_id else self.env.company.commission_based_on
                product_id = self.env['product.product'].browse(vals['product_id'])
                if commission_based_on:
                    sale_commission_percentage = []
                    if commission_based_on == 'product_category':
                        for level in product_id.categ_id.sale_commission_percentage_ids:
                            sale_commission_percentage.append(level.id)
                    elif commission_based_on == 'product_template':
                        for level in product_id.sale_commission_percentage_ids:
                            sale_commission_percentage.append(level.id)
                    vals.update({'commission_percentage_ids' : [(6, 0,sale_commission_percentage)] })
        return super(AccountInvoiceLine, self).create(vals_list)

    def write(self, vals):
        for rec in self:
            if vals.get('product_id'):
#                commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on')
                company_id = self.env['res.company'].browse(vals.get("company_id")) if vals.get("company_id") else rec.company_id if rec.company_id else False
                commission_based_on = company_id.commission_based_on if company_id else self.env.company.commission_based_on
                product_id = self.env['product.product'].browse(vals['product_id'])
                if commission_based_on:
                    sale_commission_percentage = []
                    if commission_based_on == 'product_category':
                        for level in product_id.categ_id.sale_commission_percentage_ids:
                            sale_commission_percentage.append(level.id)
                    elif commission_based_on == 'product_template':
                        for level in product_id.sale_commission_percentage_ids:
                            sale_commission_percentage.append(level.id)
                    vals.update({'commission_percentage_ids' : [(6, 0,sale_commission_percentage)] })
        return super(AccountInvoiceLine, self).write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
