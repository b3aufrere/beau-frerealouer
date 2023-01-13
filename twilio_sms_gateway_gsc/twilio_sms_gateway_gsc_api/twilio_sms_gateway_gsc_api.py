# -*- coding: utf-8 -*-
#!/usr/bin/python3
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json, requests, logging, base64
from werkzeug import urls
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

TWILIO_BASE_URL_ENDPOINT = "https://api.twilio.com"
TWILIO_RESPONSE_ENDPOINT = ".json"
# /2010-04-01/Accounts/{AccountSid}/Messages
TWILIO_SEND_SMS_URL_ENDPOINT = TWILIO_BASE_URL_ENDPOINT + "/2010-04-01/Accounts/%s/Messages" + TWILIO_RESPONSE_ENDPOINT
TWILIO_GET_ACCOUNT_DETAILS_ENDPOTINT = TWILIO_BASE_URL_ENDPOINT + "/2010-04-01/Accounts/%s" + TWILIO_RESPONSE_ENDPOINT

class TwilioSendSMSAPI():
    
    def _get_authorization_token(self, twilio_account):
        message = "%s:%s" % (twilio_account.account_sid,twilio_account.authtoken)
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message
    
    def test_twilio_sms_connection_api(self, twilio_account):
        base64_auth = self._get_authorization_token(twilio_account)
        TWILIO_SEND_SMS_URL_ENDPOINT_FINAL = TWILIO_SEND_SMS_URL_ENDPOINT % (twilio_account.account_sid)
        data = {
            "To": twilio_account.test_connection_mobile_number,
            "From": twilio_account.account_from_mobile_number,
            "Body": "Your Odoo Twilio successfully connected with Twilio.",
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic %s" % (base64_auth)
        }
        try:
            response = requests.post(TWILIO_SEND_SMS_URL_ENDPOINT_FINAL, data, headers=headers, timeout=20)
            #response.raise_for_status()
            return response
        except Exception as e:
            error_msg = _("Something went wrong while calling Send SMS API.\nRequested URL: %s\nError: %s" % (TWILIO_SEND_SMS_URL_ENDPOINT_FINAL, e))
            raise UserError(error_msg)
        
    def get_twilio_sms_account_details_api(self, twilio_account):
        base64_auth = self._get_authorization_token(twilio_account)
        TWILIO_GET_ACCOUNT_DETAILS_ENDPOTINT_FINAL = TWILIO_GET_ACCOUNT_DETAILS_ENDPOTINT % (twilio_account.account_sid)      
        try:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Basic %s" % (base64_auth),
            }
            response = requests.get(TWILIO_GET_ACCOUNT_DETAILS_ENDPOTINT_FINAL, headers=headers, timeout=20)
            #response.raise_for_status()       
            return response
        except Exception as e:
            error_msg = _("Something went wrong while calling GET Account Details SMS API.\nRequested URL: %s\nError: %s" % (TWILIO_GET_ACCOUNT_DETAILS_ENDPOTINT_FINAL, e))
            raise UserError(error_msg)
        
    def post_twilio_sms_send_to_recipients_api(self, twilio_account, datas):
        base64_auth = self._get_authorization_token(twilio_account)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic %s" % (base64_auth)
        }
        try:
            TWILIO_SEND_SMS_URL_ENDPOINT_FINAL = TWILIO_SEND_SMS_URL_ENDPOINT % (twilio_account.account_sid)
            response = requests.post(TWILIO_SEND_SMS_URL_ENDPOINT_FINAL, datas, headers=headers, timeout=20)
            return response
        except Exception as e:
            error_msg = _("Something went wrong while calling Send SMS API.\nRequested URL: %s\nError: %s" % (TWILIO_SEND_SMS_URL_ENDPOINT_FINAL, e))
            raise UserError(error_msg)
            