from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ResCompany(models.Model):
    _inherit = 'res.company'

    commission_based_on = fields.Selection([
        ('sales_team', 'Sales Team'),
        ('product_category', 'Product Category'),
        ('product_template', 'Product')], 
        string="Calculation Based On",
        default='sales_team',
    )
    when_to_pay = fields.Selection([
        ('sales_confirm', 'Sales Confirmation'),
        ('invoice_validate', 'Invoice Validate'),
        ('invoice_payment', 'Customer Payment')], 
        string="When To Pay",
        default='sales_confirm',
    )
