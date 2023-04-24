# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

from logging import warning as w

class TaskCancellationWiz(models.TransientModel):
    _name = 'task.cancellation.wiz'
    _description = 'Task cancellation wiz'
    
    task_id = fields.Many2one(
        'project.task',
        string='Tâche',
        )
    
    task_cancellation_reason_id = fields.Many2one(
        'task.cancellation.reason',
        string="Motif d'annulation",
        )
    
    def action_cancel_task(self):
        cancel_stage_id = False
        if not self.task_id.parent_id and self.task_id.project_id:
            cancel_stage_id = self.env['project.task.type'].search([('name', '=', 'Annulé'), ('project_ids', 'in', self.task_id.project_id.id)], limit=1)
        elif self.display_project_id:
            cancel_stage_id = self.env['project.task.type'].search([('name', '=', 'Annulé'), ('project_ids', 'in', self.task_id.display_project_id.id)], limit=1)
        
        if cancel_stage_id:
            self.task_id.stage_id = cancel_stage_id.id
            self.task_id.task_cancellation_reason_id = self.task_cancellation_reason_id.id
            self.task_id.user_ids = False
        else:
            raise UserError("Il faut ajouté une étape Annulé a ce projet")