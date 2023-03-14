# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CrmStage(models.Model):
    _inherit = 'crm.stage'


    mail_template_id = fields.Many2one('mail.template', string="Modèle d'email", domain=[('model', '=', 'crm.lead')])
    sms_template_id = fields.Many2one("twilio.sms.template", "Modèle de SMS", domain="[('model_id', '!=', False), ('model_id.model', '=', 'crm.lead')]", copy=False)
    mail_activity_type_id = fields.Many2one('mail.activity.type', string="Type d'activité")