from odoo import models, fields

class TwilioSendSmsGatewayAccount(models.Model):
    _inherit = 'twilio.sms.gateway.account'

    is_notify_worker_abt_his_new_task = fields.Boolean("Informer le travailleur de sa nouvelle visite par SMS ?", default=False, copy=False)
    sms_notify_worker_abt_his_new_task_template_id = fields.Many2one("twilio.sms.template", "Informer le travailleur de sa nouvelle visite SMS Template", domain="[('model_id', '!=', False), ('model_id.model', '=', 'project.task')]", copy=False)
