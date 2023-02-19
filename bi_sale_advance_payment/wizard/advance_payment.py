# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class AdvancePayment(models.TransientModel):
    _name = 'advance.payment'
    _description = 'Advance Payment'

    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True,
                                 domain=[('type', 'in', ['cash', 'bank'])])
    pay_amount = fields.Float(string="Payable Amount", required=True)
    date_planned = fields.Datetime(string="Advance Payment Date", index=True, default=fields.Datetime.now,
                                   required=True)

    @api.constrains('pay_amount')
    def check_amount(self):
        if self.pay_amount <= 0:
            raise ValidationError(_("Please Enter Postive Amount"))

    def make_payment(self):
        payment_obj = self.env['account.payment']
        purchase_ids = self.env.context.get('active_ids', [])
        if purchase_ids:
            payment_res = self.get_payment(purchase_ids)
            payment = payment_obj.create(payment_res)
            payment.action_post()
        return {
            'type': 'ir.actions.act_window_close',
        }

    def get_payment(self, purchase_ids):
        purchase_obj = self.env['sale.order']
        purchase_id = purchase_ids[0]
        purchase = purchase_obj.browse(purchase_id)
        payment_res = {
            'payment_type': 'inbound',
            'partner_id': purchase.partner_id.id,
            'partner_type': 'customer',
            'journal_id': self.journal_id.id,
            'company_id': purchase.company_id.id,
            'currency_id': purchase.currency_id.id,
            'date': self.date_planned,
            'amount': self.pay_amount,
            'sale_id': purchase.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id
        }
        return payment_res
