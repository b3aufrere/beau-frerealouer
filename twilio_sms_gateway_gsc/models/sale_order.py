# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext, plaintext2html

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        
        twilio_sms_accounts = self.env['twilio.sms.gateway.account'].sudo().search([('state', '=', 'confirmed')], order="id asc")
        tobe_twilio_sms_accounts = twilio_sms_accounts.filtered(lambda x: x.is_default_sms_account)
        twilio_sms_account = False
        if tobe_twilio_sms_accounts:
            twilio_sms_account = tobe_twilio_sms_accounts[0]
        elif twilio_sms_accounts:
            twilio_sms_account = twilio_sms_accounts[0]
        
        if twilio_sms_account and twilio_sms_account.is_confirm_so_to_send_sms and twilio_sms_account.sms_so_confirm_template_id:
            for sale in self:
                message = sale._message_sms_with_template_twilio(
                        template=twilio_sms_account.sms_so_confirm_template_id,
                        partner_ids=sale.partner_id.ids
                    )
                message = html2plaintext(message) #plaintext2html(html2plaintext(message))
                datas = {
                    "From": twilio_sms_account.account_from_mobile_number,
                    "To": (sale.partner_id.mobile or "").replace(" ", ""),
                    "Body": message
                }
                twilio_sms_account.send_sms_to_recipients_from_another_src(datas)
        return res