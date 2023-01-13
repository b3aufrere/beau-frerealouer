# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext, plaintext2html

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        
        twilio_sms_accounts = self.env['twilio.sms.gateway.account'].sudo().search([('state', '=', 'confirmed')], limit=1, order="id asc")
        tobe_twilio_sms_accounts = twilio_sms_accounts.filtered(lambda x: x.is_default_sms_account)
        twilio_sms_account = False
        if tobe_twilio_sms_accounts:
            twilio_sms_account = tobe_twilio_sms_accounts[0]
        elif twilio_sms_accounts:
            twilio_sms_account = twilio_sms_accounts[0]
        
        if twilio_sms_account and twilio_sms_account.is_validate_do_to_send_sms and twilio_sms_account.sms_do_validate_template_id:
            for picking in self:
                message = picking._message_sms_with_template_twilio(
                        template=twilio_sms_account.sms_do_validate_template_id,
                        partner_ids=picking.partner_id.ids
                    )
                message = html2plaintext(message) #plaintext2html(html2plaintext(message))
                datas = {
                    "From": twilio_sms_account.account_from_mobile_number,
                    "To": (picking.partner_id.mobile or "").replace(" ", ""),
                    "Body": message
                }
                twilio_sms_account.send_sms_to_recipients_from_another_src(datas)
        return res