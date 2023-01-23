# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    
    order_id = fields.Many2one('sale.order', string='Bon de commande')