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
]

class TwilioSendSmsGatewayAccount(models.Model):
    _name = 'twilio.sms.gateway.account'
    _description = "Twilio SMS Gateway SMS"
    
    def _compute_total_sms_data(self):
        twilio_sms_send_obj = self.env['twilio.sms.send']
        twilio_sms_log_history_obj = self.env['twilio.sms.log.history']
        for twilio_account in self:
            twilio_account.sms_records_count = len(twilio_sms_send_obj.search([('twilio_account_id', '=', twilio_account.id)]))
            twilio_account.account_sms_logs_count = len(twilio_sms_log_history_obj.search([('twilio_account_id', '=', twilio_account.id)]))
    
    name = fields.Char("Account Name", help="Account name", required=True, copy=False)
    account_sid = fields.Char("Account SID", help="Account SID", required=True, copy=False)
    authtoken = fields.Char("Authtoken", help="Authtoken", required=True, copy=False)
    account_from_mobile_number = fields.Char("From Mobile Number", help="Mobile number should be with country code.", required=True, copy=False)
    test_connection_mobile_number = fields.Char("Test Connection Mobile Number", help="Mobile number should be with country code i.e +91xxxxxxxx")
    is_default_sms_account = fields.Boolean("Is Default SMS Account?", copy=False)
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
    ], default='new', help="State")
    account_type = fields.Selection([
        ('Trial', 'Trial'),
        ('Full', 'Full'),
    ], string="Twilio Account Type", copy=False)
    account_status = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed'),
    ], string="Twilio Account Status", copy=False)
    
    is_confirm_so_to_send_sms = fields.Boolean("Confirm Order to Send SMS?", default=False, copy=False)
    sms_so_confirm_template_id = fields.Many2one("twilio.sms.template", "SMS Template", domain="[('model_id', '!=', False), ('model_id.model', '=', 'sale.order')]", copy=False)
    is_validate_do_to_send_sms = fields.Boolean("Validate Delivery to Send SMS?", default=False, copy=False)
    sms_do_validate_template_id = fields.Many2one("twilio.sms.template", "SMS Template", domain="[('model_id', '!=', False), ('model_id.model', '=', 'stock.picking')]", copy=False)
    
    # Magic button's fields
    sms_records_count = fields.Integer(string='Account SMS Records Count', compute='_compute_total_sms_data')
    account_sms_logs_count = fields.Integer(string='Account SMS Logs Count', compute='_compute_total_sms_data')
    
    # Odoo Logic Section
    # =====================
    @api.constrains('account_sid', 'authtoken')
    def _check_duplicate_twilio_account(self):
        twilio_accounts = self.search([('account_sid', '=', self.account_sid), ('authtoken', '=', self.authtoken)])
        if twilio_accounts and len(twilio_accounts) > 1:
            raise ValidationError(_('You can not create same duplicate Twilio Account with same Account SID and Authtoken.'))
        return True 
    
    def reset_to_new(self):
        for twilio_account in self:
            twilio_account.write({'state': 'new'})
        return True
    
    def action_open_sms_send_records(self):
        """
            :return: action or error
        """
        send_sms_records = self.env['twilio.sms.send'].sudo().search([('twilio_account_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(send_sms_records.ids) + " )]",
            'name': "Send SMS Records",
            'view_mode': 'tree,form',
            'res_model': 'twilio.sms.send',
            'type': 'ir.actions.act_window',
        }
        return action
    
    def action_open_sms_account_logs_records(self):
        """
            :return: action or error
        """
        account_sms_logs_records = self.env['twilio.sms.log.history'].sudo().search([('twilio_account_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(account_sms_logs_records.ids) + " )]",
            'name': "SMS Logs History",
            'view_mode': 'tree,form',
            'res_model': 'twilio.sms.log.history',
            'type': 'ir.actions.act_window',
        }
        return action
    
    # API Logic Section
    # =====================
    def test_twilio_sms_connection(self):
        if not self.test_connection_mobile_number:
            raise UserError(_("'Test Connection Mobile Number' is required for connection checking!!!"))
        
        ctx = dict(self.env.context)
        method_call = ctx.get("method_call", "")
        TwilioSendSMSAPIObj = TwilioSendSMSAPI()
        response_obj = TwilioSendSMSAPIObj.test_twilio_sms_connection_api(self)
        if response_obj.status_code in [200, 201]:
            response = response_obj.json()
            if isinstance(response, dict) and response.get('status') in SUCCESS_RESPONSE_STATUES:
                if method_call == "test_and_confirm_twilio_sms_account":
                    self.state = "confirmed"
                    self._cr.commit()
                error_msg = _("Service working properly!!! Your message sent successfully to %s" % (self.test_connection_mobile_number))
                raise UserError(error_msg)
        elif response_obj.status_code in [400]:
            response = response_obj.json()
            message = response.get("message")
            code = response.get("code")
            more_info = response.get("more_info")
            status_code = response.get("status")
            error_msg = _("Due to below reason your message is not sent to %s.\nResponse Error,\n Response Status Code: %s\n Response Message: %s\n Error Code: %s\n More Info.: %s" % (self.test_connection_mobile_number, status_code, message, code, more_info))
            raise UserError(error_msg)
        else:
            error_msg = _("Something went to wrong!!!.\nResponse Status Code: %s\nError More Info.: https://www.twilio.com/docs/api/errors"% (response_obj.status_code))
            raise UserError(error_msg)
        return True
    
    def test_and_confirm_twilio_sms_account(self):
        self.with_context({'method_call': 'test_and_confirm_twilio_sms_account'}).test_twilio_sms_connection()
        return True
    
    def get_twilio_account_details(self):
        TwilioSendSMSAPIObj = TwilioSendSMSAPI()
        response_obj = TwilioSendSMSAPIObj.get_twilio_sms_account_details_api(self) 
        if response_obj.status_code in [200, 201]:
            response = response_obj.json()
            self.write({
               'account_type': response.get('type'),
               'account_status': response.get('status'),
            })
        elif response_obj.status_code in [403]:
            response = response_obj.json()
            message = response.get("message")
            code = response.get("code")
            more_info = response.get("more_info")
            status_code = response.get("status")
            error_msg = _("Due to below reason not get account details from Twilio.\nResponse Error,\n Response Status Code: %s\n Response Message: %s\n Error Code: %s\n More Info.: %s" % (status_code, message, code, more_info))
            raise UserError(error_msg)
        else:
            error_msg = _("Something went to wrong!!!.\nResponse Status Code: %s\nError More Info.: https://www.twilio.com/docs/api/errors"% (response_obj.status_code))
            raise UserError(error_msg)
        return True
    
    def send_sms_to_recipients_from_another_src(self, datas):
        """
            This function to send SMS from another sources such as Sales, Picking,...etc
            :return: True or Error
        """
        twilio_sms_log_history_obj = self.env['twilio.sms.log.history']
        twilioSendSMSAPIObj = TwilioSendSMSAPI()
        
        response_obj = twilioSendSMSAPIObj.post_twilio_sms_send_to_recipients_api(self, datas)        
        if response_obj.status_code in [200, 201]:
            response = response_obj.json()
            twilio_sms_log_history_obj.create({
                'twilio_account_id': self.id,
                'message_id': response.get("sid"),
                'mobile_number': response.get("to"),
                'message': response.get("body"),
                'status': response.get("status"),
                'message_price': response.get("price", 0.0),
            })
        elif response_obj.status_code in [400]:
            response = response_obj.json()
            twilio_sms_log_history_obj.create({
                'twilio_account_id': self.id,
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
                'twilio_account_id': self.id,
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
        return True