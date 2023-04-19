# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TaskReassignment(models.Model):
    _name = 'task.reassignment'
    _description = 'Réassignation de tâche'

    user_id = fields.Many2one(
        'res.users',
        string='Assigné',
        )
    
    task_id = fields.Many2one(
        'project.task',
        string='Tâche',
        )
    
    def action_reassign_task(self):
        new_stage_id = False
        if not self.task_id.parent_id and self.task_id.project_id:
            new_stage_id = self.env['project.task.type'].search([('name', '=', 'Nouveau'), ('project_ids', 'in', self.task_id.project_id.id)], limit=1)
        elif self.display_project_id:
            new_stage_id = self.env['project.task.type'].search([('name', '=', 'Nouveau'), ('project_ids', 'in', self.task_id.display_project_id.id)], limit=1)
        
        if new_stage_id:
            self.task_id.stage_id = new_stage_id.id
            self.task_id.user_ids = [(6, 0, [self.user_id.id])]
        else:
            raise UserError("Il faut ajouté une étape Nouveau a ce projet")