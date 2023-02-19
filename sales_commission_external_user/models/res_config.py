# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
#from openerp.exceptions import Warning
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
#     _inherit = 'sale.config.settings'
    _inherit = 'res.config.settings' #odoo11

    commission_based_on = fields.Selection([
        ('sales_team', 'Sales Team'),
        ('product_category', 'Product Category'),
        ('product_template', 'Product')], 
        string="Calculation Based On",
        related="company_id.commission_based_on",
        readonly=False,
    )
    when_to_pay = fields.Selection([
        ('sales_confirm', 'Sales Confirmation'),
        ('invoice_validate', 'Invoice Validate'),
        ('invoice_payment', 'Customer Payment')], 
        string="When To Pay",
        related="company_id.when_to_pay",
        readonly=False,
    )
    
#     @api.multi
#     def set_commission_based_on_defaults(self):
#         if self.when_to_pay == 'invoice_payment':
#             if self.commission_based_on == 'product_category' or self.commission_based_on == 'product_template':
#                 raise UserError(_("Sales Commission: You can not have commision based on product or category if you have selected when to pay is payment."))
#         return self.env['ir.values'].sudo().set_default(
#             'sale.config.settings', 'commission_based_on', self.commission_based_on)
# 
#     @api.multi
#     def set_when_to_pay_defaults(self):
#         return self.env['ir.values'].sudo().set_default(
#             'sale.config.settings', 'when_to_pay', self.when_to_pay)

#    @api.model
#    def get_values(self):
#        res = super(ResConfigSettings, self).get_values()
#        params = self.env['ir.config_parameter'].sudo()
#        res.update(
#            when_to_pay = params.get_param('sales_commission_external_user.when_to_pay'),
#            commission_based_on = params.get_param('sales_commission_external_user.commission_based_on')
#        )
#        return res

##    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("sales_commission_external_user.when_to_pay", self.when_to_pay)
        if not self.env.context.get('skip'): #odoo11 skip real_estate_property_app
            if self.when_to_pay == 'invoice_payment':
                if self.commission_based_on == 'product_category' or self.commission_based_on == 'product_template':
                    raise UserError(_("Sales Commission: You can not have commision based on product or category if you have selected when to pay is payment."))
#                    raise UserError(_("Sales Commission: You can not have commision based on product or category if you have selected when to pay is payment."))
        ICPSudo.set_param("sales_commission_external_user.commission_based_on", self.commission_based_on)
