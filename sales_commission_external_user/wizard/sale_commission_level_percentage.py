# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleCommissionPercentage(models.TransientModel):
    _name = "sale.commission.level.percentage.wiz"

    level_id = fields.Many2one(
        'sale.commission.level',
        string="Commission Level",
        required=True,
    )
    percentage = fields.Float(
        string='Percentage (%)',
        required=True,
    )
    payment_reg_id = fields.Many2one(
        'account.payment.register',
        string="Account Payment"
    )

    @api.model
    def create(self, vals):
        return super(SaleCommissionPercentage, self.sudo()).create(vals)

    @api.constrains('percentage')
    def _percentage_validation(self):
        for percentage in self:
            if percentage.percentage:
                if percentage.percentage < 0.0 or percentage.percentage > 100.0:
                    raise ValidationError(_('Percentage must be between 0.0 to 100.0!'))

    @api.constrains('level_id')
    def _level_validation(self):
        for level in self:
            domain = [('level_id', '=', level.level_id.id)]
            if level.payment_reg_id:
                domain.append(('payment_reg_id','=',level.payment_reg_id.id))

            level_ids = self.search_count(domain)
            if level_ids > 1:
                raise ValidationError(_('Commission Levels must be unique!'))
