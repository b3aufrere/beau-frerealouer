# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.twilio_sms_gateway_gsc.twilio_sms_gateway_gsc_api.twilio_sms_gateway_gsc_api import TwilioSendSMSAPI

import logging
_logger = logging.getLogger(__name__)

SUCCESS_RESPONSE_STATUES = [
    'accepted',
    'queued',
    'sending',
    'sent',
    'delivered'
]
ERROR_RESPONSE_STATUES = [
    'undelivered',
    'failed',
    'error'
]

class TwilioSmsSend(models.Model):
    _name = 'twilio.sms.send'
    _description = "Twilio SMS Send"
    _order = 'id DESC'
    
    @api.depends('recipients')
    def _compute_total_recipients(self):
        for sms_id in self:
            if sms_id.send_sms_to == "single_contact":
                sms_id.recipients_count = len(sms_id.partner_id)
            elif sms_id.send_sms_to == "multiple_contacts":
                sms_id.recipients_count = len(sms_id.partner_ids)
            elif sms_id.send_sms_to == "sms_group":
                sms_id.recipients_count = len(sms_id.sms_group_id.recipients)
            else:
                sms_id.recipients_count = 0
    
    def _compute_twilio_response_data(self):
        for sms_id in self:
            sms_id.total_messages = len(sms_id.sms_log_history_ids)
            sms_id.total_successfully_send_messages = len(sms_id.sms_log_history_ids.filtered(lambda x: x.status in SUCCESS_RESPONSE_STATUES))
            sms_id.total_error_messages = len(sms_id.sms_log_history_ids.filtered(lambda x: x.status not in SUCCESS_RESPONSE_STATUES))
            sms_id.total_price = sum(sms_id.sms_log_history_ids.mapped("message_price"))
            
    SEND_SMS_TO_SELECTIONS = [
        ('single_contact', 'Contact'),
        ('multiple_contacts', 'Multiple Contacts'),
        ('sms_group', 'SMS Group'),
        ('mobile', 'Mobile'),
    ]
    STATUS_SELECTION = [
        ('draft', 'Draft'),
        ('done', 'Sent'),
        ('error', 'Error'),
    ]
    
    name = fields.Char("SMS ID", help="ID", copy=False)
    twilio_account_id = fields.Many2one("twilio.sms.gateway.account", "SMS Account", domain="[('state', '=', 'confirmed')]",help="SMS Account")
    send_sms_to = fields.Selection(SEND_SMS_TO_SELECTIONS, "Send SMS To", default="single_contact")
    partner_id = fields.Many2one("res.partner", "Contact")
    partner_ids = fields.Many2many("res.partner", "twilio_sms_send_partners_rel", "twilio_sms_send_id", "partner_id", "Contacts")
    sms_group_id = fields.Many2one("twilio.sms.groups", "SMS Group")
    mobile_number = fields.Char("Mobile (With Country Code)", help="Mobile number (With Country Code)")
    message = fields.Text("Message", help="Message")
    recipients_count = fields.Integer(string='recipients Count', compute='_compute_total_recipients')
    recipients = fields.Many2many("res.partner", 'twilio_sms_send_res_partners_rel', 'sms_send_id', 'partner_id',
                                    "Recipients", required=True)
    sms_log_history_ids = fields.One2many("twilio.sms.log.history", "sms_send_rec_id", "SMS Log History")
    total_price = fields.Float("Total Price", compute="_compute_twilio_response_data")
    total_messages = fields.Integer("Total No. of Messages", compute="_compute_twilio_response_data")
    total_successfully_send_messages = fields.Integer("Total Successfully Send Messages", compute="_compute_twilio_response_data")
    total_error_messages = fields.Integer("Total No. Error Messages", compute="_compute_twilio_response_data")
    state = fields.Selection(STATUS_SELECTION, string="Status", readonly=True, copy=False, default='draft', required=True)
    sms_template_id = fields.Many2one("twilio.sms.template", "SMS Template", domain="[('model_id', '=', False)]", copy=False,)

    error_code = fields.Char("Error Code", copy=False)
    error_message = fields.Char("Error Message", copy=False)
    error_status_code = fields.Char("Error Status Code", copy=False)
    error_more_info = fields.Char("Error More Info", copy=False)

    # Odoo Logic Section
    # =====================    
    @api.model
    def create(self, vals):
        seq_id = self.env['ir.sequence'].next_by_code('odoo.twilio.sms.send.seq')
        vals.update({'name': seq_id })
        return super(TwilioSmsSend, self).create(vals)
    
    def unlink(self):
        for rec in self:
            if rec.state == "done":
                error_message = _("You can not delete SMS record which is in Sent State.")
                raise UserError(error_message)
    
    @api.onchange("sms_template_id")
    def onchange_sms_template_id(self):
        if self.sms_template_id:
            self.message = self.sms_template_id.message
        else:
            self.message = ""
            
    def action_view_recipients(self):
        """
            :return: action or error
        """
        recipients = []
        if self.send_sms_to == "single_contact":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.partner_id.ids)])
        elif self.send_sms_to == "multiple_contacts":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.partner_ids.ids)])
        elif self.send_sms_to == "sms_group":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.sms_group_id.recipients.ids)])
        
        action = {
            'domain': "[('id', 'in', " + str(recipients.ids) + " )]",
            'name': "Recipients",
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
        }
        return action
    
    def send_sms_to_recipients(self, datas):
        twilio_sms_log_history_obj = self.env['twilio.sms.log.history']
        twilioSendSMSAPIObj = TwilioSendSMSAPI()
        twilio_account_id = self.twilio_account_id
        response_obj = twilioSendSMSAPIObj.post_twilio_sms_send_to_recipients_api(self.twilio_account_id, datas)        
        if response_obj.status_code in [200, 201]:
            response = response_obj.json()
            twilio_sms_log_history_obj.create({
                'sms_send_rec_id': self.id,
                'twilio_account_id': twilio_account_id.id,
                'message_id': response.get("sid"),
                'mobile_number': response.get("to"),
                'message': response.get("body"),
                'status': response.get("status"),
                'message_price': response.get("price", 0.0),
            })
        elif response_obj.status_code in [400]:
            response = response_obj.json()
            twilio_sms_log_history_obj.create({
                'sms_send_rec_id': self.id,
                'twilio_account_id': twilio_account_id.id,
                'message_id': "",
                'mobile_number': datas.get("To"),
                'message': datas.get("Body"),
                'status': "Error",
                'message_price': 0.0,
                'error_code': response.get('code'),
                'error_message': response.get('message'),
                'error_status_code': response.get('status'),
                'error_more_info': response.get('more_info'),
            })
        elif response_obj.status_code in [401]:
            response = response_obj.json()
            twilio_sms_log_history_obj.create({
                'sms_send_rec_id': self.id,
                'twilio_account_id': twilio_account_id.id,
                'message_id': "",
                'mobile_number': datas.get("To"),
                'message': datas.get("Body"),
                'status': "Error",
                'message_price': 0.0,
                'error_code': response.get('code'),
                'error_message': response.get('message'),
                'error_status_code': response.get('status'),
                'error_more_info': response.get('more_info'),
            })
            return False, response
        return True, ""
    
    def action_send_sms_to_recipients(self):
        twilio_account_id = self.twilio_account_id
        send_sms_to = self.send_sms_to
        error_message = ""
        if not twilio_account_id:
            error_message = _("SMS Account is required so select Account and try again to Send Message.")
            raise UserError(error_message)
        if not send_sms_to:
            error_message = _("Send SMS To is required so select Send SMS To and try again to Send Message.")
            raise UserError(error_message)
        
        twilio_account_from_number = twilio_account_id.account_from_mobile_number
        message = self.message
        result = False
        
        if self.send_sms_to == "single_contact":
            datas = {
                "From": twilio_account_from_number,
                "To": (self.partner_id.mobile or "").replace(" ", ""),
                "Body": message
            }
            result, response = self.send_sms_to_recipients(datas)
        elif self.send_sms_to == "multiple_contacts":
            for partner_id in self.partner_ids:
                datas = {
                    "From": twilio_account_from_number,
                    "To": (partner_id.mobile or "").replace(" ", ""),
                    "Body": message
                }
                result, response = self.send_sms_to_recipients(datas)
                if not result:
                    break
        elif self.send_sms_to == "sms_group":
            for partner_id in self.sms_group_id.recipients:
                datas = {
                    "From": twilio_account_from_number,
                    "To": (partner_id.mobile or "").replace(" ", ""),
                    "Body": message
                }
                result, response = self.send_sms_to_recipients(datas)
                if not result:
                    break
        elif self.mobile_number:
            datas = {
                "From": twilio_account_from_number,
                "To": (self.mobile_number or "").replace(" ", ""),
                "Body": message
            }
            result, response = self.send_sms_to_recipients(datas)
        if result:
            self.write({
                'state': 'done',
            })
        elif not result:
            self.write({
                'state': 'error',
                'error_code': response.get('code'),
                'error_message': response.get('message'),
                'error_status_code': response.get('status'),
                'error_more_info': response.get('more_info'),
            })
        return True