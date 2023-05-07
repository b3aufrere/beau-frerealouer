# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

from logging import warning as w

class OrderNotAcceptWiz(models.TransientModel):
    _name = 'order.not.accept.wiz'
    _description = 'Order not accept wiz'
    
    order_id = fields.Many2one(
        'sale.order',
        string='Soumission',
        )
    
    order_not_accept_reason_id = fields.Many2one(
        'order.not.accept.reason',
        string="Motif de non acceptation",
        )
    
    def action_not_accept_order(self):
        self.order_id.state = "not_accepted"
        self.order_id.order_not_accept_reason_id = self.order_not_accept_reason_id.id
        self.order_id.user_id = False