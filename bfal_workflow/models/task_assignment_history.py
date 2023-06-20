# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TaskAssignmentHistory(models.Model):
    _name = 'task.assignment.history'
    _description = 'Task assignment history'

    
    user_ids = fields.Many2many('res.users', string='Assignés')
    task_id = fields.Many2one('project.task', string='Tâche')
    order_id = fields.Many2one('sale.order', string='Devis')
    motif = fields.Char(string="Motif")