# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class OrderNotAcceptReason(models.Model):
    _name = 'order.not.accept.reason'
    _description = 'Order not accept reason'

    name = fields.Char(string="Motif", required=True)