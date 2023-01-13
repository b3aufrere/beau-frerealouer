# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class TwilioSMSLogHistory(models.Model):
    _name = 'twilio.sms.log.history'
    _description = "Twilio SMS Log History"
    _order = 'id DESC'
    
    name = fields.Char("Log ID", copy=False, help="LOG ID")
    sms_send_rec_id =  fields.Many2one("twilio.sms.send", "SMS Send ID", copy=False)
    twilio_account_id = fields.Many2one("twilio.sms.gateway.account", "SMS Account ID", copy=False)
    partner_id = fields.Many2one("res.partner", "Contact", copy=False)
    mobile_number = fields.Char("Mobile No.", copy=False)
    message_id = fields.Char("Message SID", copy=False)
    message = fields.Text("Message", copy=False)
    status = fields.Char("Status", copy=False)
    message_price = fields.Float("Message Price", copy=False)
    
    error_code = fields.Char("Error Code", copy=False)
    error_message = fields.Char("Error Message", copy=False)
    error_status_code = fields.Char("Error Status Code", copy=False)
    error_more_info = fields.Char("Error More Info", copy=False)
    
    
    @api.model
    def create(self, vals):
        seq_id = self.env['ir.sequence'].next_by_code('odoo.twilio.sms.log.history.seq')
        vals.update({'name': seq_id })
        return super(TwilioSMSLogHistory, self).create(vals)
    
    