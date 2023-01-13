# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class TwilioSendSMSTemplate(models.Model):
    _name = 'twilio.sms.template'
    _inherit = ['mail.render.mixin']
    _description = "Twilio SMS Template"
    
    name = fields.Char("Template Name", help="SMS template name", required=True, copy=False)
    active = fields.Boolean("Active", default=True)
    message = fields.Text("Message", help="message")
    model_id = fields.Many2one('ir.model', 'Applies to', domain="[('model', 'in', ['sale.order', 'stock.picking'])]", help="The type of document this template can be used with")
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    
    # Overrides of mail.render.mixin
    @api.depends('model_id')
    def _compute_render_model(self):
        res = super(TwilioSendSMSTemplate, self)._compute_render_model()
        for template in self:
            template.render_model = template.model
        return res