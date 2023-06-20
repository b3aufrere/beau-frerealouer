# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class SaleCommissionUsers(models.TransientModel):
    _name = "sale.commission.level.users.wiz"

    level_id = fields.Many2one(
        'sale.commission.level',
        string="Commission Level",
        required=True,
    )
    user_id = fields.Many2one(
        'res.partner',
        string="Internal User/ External Partner",
    )
    payment_reg_id = fields.Many2one(
        'account.payment.register',
        string="Account Payment"
    )

    @api.model
    def create(self, vals):
        return super(SaleCommissionUsers, self.sudo()).create(vals)
    
    @api.constrains('level_id')
    def _level_validation(self):
        for level in self:
            if level.level_id:
                domain = [('level_id', '=', level.level_id.id)]
                if level.payment_reg_id:
                    domain.append(('payment_reg_id','=',level.payment_reg_id.id))
                level_ids = self.search_count(domain)
                if level_ids > 1:
                    raise ValidationError(_('You can not set multiple level!'))
