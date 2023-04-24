# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TaskCancellationReason(models.Model):
    _name = 'task.cancellation.reason'
    _description = 'Cancellation reason'

    name = fields.Char(string="Motif", required=True)