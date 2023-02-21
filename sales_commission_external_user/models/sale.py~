# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError, ValidationError
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def _get_is_apply(self):
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
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

    @api.multi
    @api.depends()
    def _compute_is_apply(self):
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        for rec in self:
            if commission_based_on == 'sales_team':
                rec.is_apply = True

    @api.multi
    @api.onchange('team_id')
    def team_id_change(self):
        for rec in self:
            sale_commission_percentage = []
            for level in rec.sudo().team_id.sale_commission_percentage_ids:
                sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                        'percentage': level.percentage,
                                        'sale_order_id':rec.id}))
            rec.sale_commission_percentage_ids = sale_commission_percentage

    @api.multi
    @api.onchange('partner_id')
    def partner_id_change(self):
        for rec in self:
            sale_commission = []
            for level in rec.partner_id.sale_commission_user_ids:
                sale_commission.append((0,0,{'level_id': level.level_id.id,
                                        'user_id': level.user_id.id,
                                        'order_id':rec.id}))
            rec.sale_commission_user_ids = sale_commission
            rec.sale_commission_percentage_ids = sale_commission

    @api.multi
    def get_categorywise_commission(self):
        for rec in self:
            commission = {}
            for line in rec.order_line:
                for commission_id in line.sale_commission_percentage_ids:
                    for partner in rec.sale_commission_user_ids:
                        if partner.level_id == commission_id.level_id:
                            amount = (line.price_subtotal * commission_id.percentage)/100
                            if partner.user_id not in commission:
                                commission[partner.user_id] = 0.0
                            commission[partner.user_id] += amount
        return commission

    @api.multi
    def get_productwise_commission(self):
        for rec in self:
            commission = {}
            for line in rec.order_line:
                for commission_id in line.sale_commission_percentage_ids:
                    for partner in rec.sale_commission_user_ids:
                        if partner.level_id == commission_id.level_id:
                            amount = (line.price_subtotal * commission_id.percentage)/100
                            if partner.user_id not in commission:
                                commission[partner.user_id] = 0.0
                            commission[partner.user_id] += amount
        return commission
    
    @api.multi
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

    @api.multi
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
                                'user_id':user.id,
                                'product_id': product.id,
                                'date' : order.confirmation_date,
                                'src_order_id': order.id,
                                'sales_commission_id':commission.id,
                                'sales_team_id': order.team_id and order.team_id.id or False,
                            }
                            commission_id = commission_obj.sudo().create(commission_value)
                            order.commission_person_id = commission_id.id
        return True

    @api.multi
    def create_base_commission(self, user):
        commission_obj = self.env['sales.commission']
        product = self.env['product.product'].search([('is_commission_product','=',1)],limit=1)
        if user:
            for order in self:
                today = date.today()
                first_day = today.replace(day=1)
                last_day = datetime.datetime(today.year,today.month,1)+relativedelta(months=1,days=-1)
                commission_value = {
                        'start_date' : first_day,
                        'end_date': last_day,
                        'product_id':product.id,
                        'commission_user_id': user.id,
                    }
                commission_id = commission_obj.sudo().create(commission_value)
            return commission_id

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
        if  when_to_pay == 'sales_confirm':
            commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
            for order in self:
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
                        ('state','=','draft')], limit=1)
                    if not commission:
                        commission = order.create_base_commission(user)
                    if  commission:
                        order.create_commission(user_commission, commission)
        return res

    @api.multi
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

    @api.multi
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
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
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
        string="Sale Commission Level Percentage"
    )

    @api.multi
    @api.depends()
    def _compute_is_apply(self):
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        for rec in self:
            when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
            if commission_based_on != 'sales_team' and when_to_pay == 'sales_confirm':
                rec.is_apply = True

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
#         when_to_pay = self.env['ir.values'].get_default('sale.config.settings', 'when_to_pay')
#         if  when_to_pay == 'sales_confirm':
        commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
        for rec in self:
            sale_commission_percentage = []
            if commission_based_on == 'product_category':
                for level in rec.product_id.categ_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                            'percentage': level.percentage,
                                            'sale_order_line_id':rec.id}))
            elif commission_based_on == 'product_template':
                for level in rec.product_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                            'percentage': level.percentage,
                                            'sale_order_line_id':rec.id}))
            rec.sale_commission_percentage_ids = sale_commission_percentage
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.sale_commission_percentage_ids:
            sale_commission_percentage_lines = []
            for commission in self.sale_commission_percentage_ids:
                sale_commission_percentage_lines.append((0, 0, {
                    'level_id': commission.level_id.id,
                    'percentage': commission.percentage}))
            vals.update({'sale_commission_percentage_ids': sale_commission_percentage_lines})
        else:#FIX 12 Sep 2017 - Default Template issue. SETH Saheb
            commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
            sale_commission_percentage = []
            if commission_based_on == 'product_category':
                for level in self.product_id.categ_id.sale_commission_percentage_ids:
                    sale_commission_percentage.append((0, 0, {
                        'level_id': level.level_id.id,
                        'percentage': level.percentage}))
            elif commission_based_on == 'product_template':
                for level in self.product_id.sale_commission_percentage_ids:
                        sale_commission_percentage.append((0, 0, {
                        'level_id': level.level_id.id,
                        'percentage': level.percentage}))
            vals.update({'sale_commission_percentage_ids': sale_commission_percentage})       
        return vals
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
