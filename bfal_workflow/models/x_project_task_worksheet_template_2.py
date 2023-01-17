# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class XProjectTaskWorksheetTemplate2(models.Model):
    _inherit = 'x_project_task_worksheet_template_2'

    date_time = fields.Datetime(default=fields.Datetime.now(), string="Date & Temps")