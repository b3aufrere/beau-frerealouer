# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    #@api.multi
    @api.depends()
    def _compute_is_apply(self):
#         commission_based_on = self.env['ir.values'].get_default('sale.config.settings', 'commission_based_on')
#        commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11
        commission_based_on = self.company_id.commission_based_on if self.company_id else self.env.company.commission_based_on
        for rec in self:
            rec.is_apply = False
            if commission_based_on == 'product_template':
                rec.is_apply = True
                
#     sales_manager_commission = fields.Float(
#         'Sales Manager Commission(%)'
#     )
#     sales_person_commission = fields.Float(
#         'Sales Person Commission(%)'
#     )
    is_commission_product = fields.Boolean(
        'Is Commission Product ?'
    )
    is_apply = fields.Boolean(
        string='Is Apply ?',
        compute='_compute_is_apply'
    )
    sale_commission_percentage_ids = fields.One2many(
        'sale.commission.level.percentage',
        'product_id',
        string="Sale Commission Level Percentage"
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
