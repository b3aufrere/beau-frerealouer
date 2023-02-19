# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleCommissionPercentage(models.Model):
    _inherit = "sale.commission.level.percentage"

    payment_product_line_id = fields.Many2one(
        'account.payment.product.lines',
        string="Account Payment Product"
    )

    @api.constrains('level_id')
    def _level_validation(self):
        super(SaleCommissionPercentage, self)._level_validation()
        for level in self:
            domain = [('level_id', '=', level.level_id.id)]
#            if level.sale_order_line_id:
            if level.payment_product_line_id:
                domain.append(('payment_product_line_id','=',level.payment_product_line_id.id))

                level_ids = self.search_count(domain)
                if level_ids > 1:
                    raise ValidationError(_('Commission Levels must be unique!'))
