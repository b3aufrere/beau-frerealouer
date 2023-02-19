# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class SaleCommissionUsers(models.Model):
    _name = "sale.commission.level.users"

    level_id = fields.Many2one(
        'sale.commission.level',
        string="Commission Level",
        required=True,
    )
    user_id = fields.Many2one(
        'res.partner',
        string="Internal User/ External Partner",
    )
    partner_id =fields.Many2one(
        'res.partner',
        string="Partner"
    )
    order_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )
#    account_id = fields.Many2one(
#        'account.invoice',
#        string="Account Invoice"
#    )
    account_id = fields.Many2one(
        'account.move',
        string="Account Invoice"
    )
    payment_id = fields.Many2one(
        'account.payment',
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
                if level.order_id:
                    domain.append(('order_id','=',level.order_id.id))
                elif level.account_id:
                    domain.append(('account_id','=',level.account_id.id))
                elif level.payment_id:
                    domain.append(('payment_id','=',level.payment_id.id))
                elif level.partner_id:
                    domain.append(('partner_id','=',level.partner_id.id))
                level_ids = self.search_count(domain)
                if level_ids > 1:
                    raise ValidationError(_('You can not set multiple level!'))
