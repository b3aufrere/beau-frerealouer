# -*- coding: utf-8 -*-
#from openerp import models, fields, api
from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = "product.category"
    
    #@api.multi
    @api.depends()
    def _compute_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.env.company.commission_based_on
        for rec in self:
            rec.is_apply = False
            if commission_based_on == 'product_category':
                rec.is_apply = True

#     sales_manager_commission = fields.Float(
#         'Sales Manager Commission(%)',
#     )
#     sales_person_commission = fields.Float(
#         'Sales Person Commission(%)',
#     )
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply',
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'product_category_id',
        string="Sale Commission Level Percentage"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
