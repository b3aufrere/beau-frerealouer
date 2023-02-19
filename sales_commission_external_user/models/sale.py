# -*- coding: utf-8 -*-

#from openerp import models, fields, api
#from openerp.exceptions import UserError, ValidationError
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
#from openerp.exceptions import UserError, ValidationError
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def _get_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.company_id.commission_based_on
        if commission_based_on == 'sales_team':
            return True

#     commission_manager_id = fields.Many2one(
#         'sales.commission.line',
#         string='Sales Commission for Manager'
#     )
#     commission_person_id = fields.Many2one(
#         'sales.commission.line',
#         string='Sales Commission for Member'
#     )
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )
    sale_commission_user_ids = fields.One2many(
        'sale.commission.level.users',
        'order_id',
        string="Sale Commission User"
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'sale_order_id',
        string="Sale Commission Level Percentage"
    )   

    #@api.multi
    @api.depends()
    def _compute_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.company_id.commission_based_on
        for rec in self:
            rec.is_apply = False
            if commission_based_on == 'sales_team':
                rec.is_apply = True

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
#            rec.sale_commission_percentage_ids = rec.sale_commission_percentage_ids - exist_sale_commission_percentage_ids #12/09/2019

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
            # rec.sale_commission_percentage_ids = sale_commission #12/09/2019

#    @api.model
#    def create(self, vals):
#        res = super(SaleOrder, self).create(vals)
#        sale_commission_percentage = []
#        if res.is_apply and res.team_id:
#            for level in res.team_id.sale_commission_percentage_ids:
#                sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
#                                        'percentage': level.percentage,
#                                        'sale_order_id':res.id}))
            # res.sale_commission_percentage_ids = sale_commission_percentage #12/09/2019
#        return res

    #@api.multi
    def get_categorywise_commission(self):
        for rec in self:
            commission = {}
            for line in rec.order_line:
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
            for line in rec.order_line:
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
            for order in self:
                if user_commission:
                    for sale_commission in commission.commission_user_id:
                        if user.id == sale_commission.id:
                            commission_value = {
                                'commission_user_id': user.id,
                                'amount':  user_commission[user],
                                'origin': order.name,
                                #'user_id':user.id,
                                'product_id': product.id,
#                                'date' : order.confirmation_date,
                                'date' : order.date_order,
                                'src_order_id': order.id,
                                'sales_commission_id':commission.id,
                                'sales_team_id': order.team_id and order.team_id.id or False,
                                'company_id': order.company_id.id,
                                'currency_id': order.company_id.currency_id.id,
                            }
                            commission_id = commission_obj.sudo().create(commission_value)
#                            order.commission_person_id = commission_id.id
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
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
#         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#        when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.when_to_pay') #odoo11
        when_to_pay = self.env.company.when_to_pay
        if  when_to_pay == 'sales_confirm':
#             commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#            commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
            for order in self:
                commission_based_on = order.company_id.commission_based_on
                if commission_based_on == 'sales_team':
                    user_commission = order.get_teamwise_commission()
                elif commission_based_on == 'product_category':
                    user_commission = order.get_categorywise_commission()
                elif commission_based_on == 'product_template':
                    user_commission = order.get_productwise_commission()
                for user in user_commission:
                    commission = self.env['sales.commission'].search([
                        ('commission_user_id', '=', user.id),
                        ('start_date', '<', order.date_order),
                        ('end_date', '>', order.date_order),
                        ('state','=','draft'),
                        ('company_id', '=', order.company_id.id),
                        ], limit=1)
                    if not commission:
                        commission = order.create_base_commission(user)
                    if  commission:
                        order.create_commission(user_commission, commission)
        return res

    #@api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        commission_obj = self.env['sales.commission.line']
        for rec in self:
            lines = commission_obj.sudo().search([('src_order_id', '=', rec.id)])
            for line in lines:
                if line.state == 'draft' or line.state == 'cancel':
                    line.state = 'exception'
                elif line.state in ('paid', 'invoice'):
                    raise UserError(_('You can not cancel this invoice because sales commission is invoiced/paid. Please cancel related commission lines and try again.'))
#             if rec.commission_manager_id:
 #                rec.commission_manager_id.state = 'exception'
  #           if rec.commission_person_id:
   #              rec.commission_person_id.state = 'exception'
        return res

    #@api.multi
    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        if self.sale_commission_user_ids:
            sale_commission_user_lines = []
            for commission in self.sale_commission_user_ids:
                sale_commission_user_lines.append((0, 0, {
                    'level_id': commission.level_id.id,
                    'user_id': commission.user_id and commission.user_id.id or False}))
            vals.update({'sale_commission_user_ids': sale_commission_user_lines})

        if self.sale_commission_percentage_ids:
            sale_commission_lines = []
            for commission in self.sale_commission_percentage_ids:
                sale_commission_lines.append((0, 0, {
                    'level_id': commission.level_id.id,
                    'percentage': commission.percentage}))
            vals.update({'sale_commission_percentage_ids': sale_commission_lines})
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _get_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.company_id.commission_based_on
#         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#        when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.when_to_pay') #odoo11
        when_to_pay = self.company_id.when_to_pay if self.company_id else self.env.company.when_to_pay
        if commission_based_on != 'sales_team' and when_to_pay == 'sales_confirm':
            return True

    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
        default=_get_is_apply
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'sale_order_line_id',
        string="Sale Commission Level Percentage",
        compute='_compute_sale_commission_percentage_ids',
        store = True
    )

    commission_percentage_ids = fields.Many2many(
        'sale.commission.level.percentage',
        string="Commission Level Percentage",
    ) #odoo11

    #@api.multi
    @api.depends()
    def _compute_sale_commission_percentage_ids(self):
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        for rec in self:
            commission_based_on = rec.company_id.commission_based_on
            sale_commission_percentage = []
            if commission_based_on == 'product_category':
                for level in rec.product_id.categ_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                            'percentage': level.percentage}))
            elif commission_based_on == 'product_template':
                for level in rec.product_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                            'percentage': level.percentage}))
            rec.sale_commission_percentage_ids = sale_commission_percentage

    #@api.multi
    @api.depends()
    def _compute_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        for rec in self:
            commission_based_on = rec.company_id.commission_based_on
            rec.is_apply = False
#             when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#            when_to_pay = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.when_to_pay') #odoo11
            when_to_pay = rec.company_id.when_to_pay
            if commission_based_on != 'sales_team' and when_to_pay == 'sales_confirm':
                rec.is_apply = True

    #@api.multi
    @api.onchange('product_id')
    # def product_id_change(self):
    def custom_product_id_change(self):
        # res = super(SaleOrderLine, self).product_id_change()
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on')
        for rec in self:
            sale_commission_percentage = []
            commission_based_on = rec.company_id.commission_based_on if rec.company_id else rec.order_id.company_id.commission_based_on
            if commission_based_on == 'product_category':
                for level in rec.product_id.categ_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append(level.id)
            elif commission_based_on == 'product_template':
                for level in rec.product_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append(level.id)
            rec.commission_percentage_ids = [(6, 0,sale_commission_percentage)]
        # return res


#     #@api.multi
#     @api.onchange('product_id')
#     def product_id_change(self):
#         res = super(SaleOrderLine, self).product_id_change()
# #         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
# #         if  when_to_pay == 'sales_confirm':
# #         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#         commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
#         for rec in self:
#             sale_commission_percentage = []
#             if commission_based_on == 'product_category':
#                 for level in rec.product_id.categ_id.sale_commission_percentage_ids:
#                     sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
#                                             'percentage': level.percentage,
#                                             'sale_order_line_id':rec.id}))
#             elif commission_based_on == 'product_template':
#                 for level in rec.product_id.sale_commission_percentage_ids:
#                     sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
#                                             'percentage': level.percentage,
#                                             'sale_order_line_id':rec.id}))
#             rec.sale_commission_percentage_ids = sale_commission_percentage
#         return res

    #@api.multi
#    def _prepare_invoice_line(self, qty):
    def _prepare_invoice_line(self, **optional_values):
#        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        vals = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.sale_commission_percentage_ids:
            sale_commission_percentage_lines = []
            for commission in self.sale_commission_percentage_ids:
                sale_commission_percentage_lines.append((0, 0, {
                    'level_id': commission.level_id.id,
                    'percentage': commission.percentage}))
            vals.update({'sale_commission_percentage_ids': sale_commission_percentage_lines})
        else:#FIX 12 Sep 2017 - Default Template issue. SETH Saheb
#             commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#            commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
            commission_based_on = self.company_id.commission_based_on
            sale_commission_percentage = []
            if commission_based_on == 'product_category':
                for level in self.product_id.categ_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append(level.id) #odoo11
#                     sale_commission_percentage.append((0, 0, {
#                         'level_id': level.level_id.id,
#                         'percentage': level.percentage}))
            elif commission_based_on == 'product_template':
                for level in self.product_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append(level.id) #odoo11
#                         sale_commission_percentage.append((0, 0, {
#                         'level_id': level.level_id.id,
#                         'percentage': level.percentage}))
            vals.update({
#                 'sale_commission_percentage_ids': sale_commission_percentage,
                'commission_percentage_ids': [(6, 0,sale_commission_percentage)] #odoo11
            })
        return vals
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
