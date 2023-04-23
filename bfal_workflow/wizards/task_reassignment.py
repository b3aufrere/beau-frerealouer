# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json

class TaskReassignment(models.Model):
    _name = 'task.reassignment'
    _description = 'Réassignation de tâche'

    def get_only_not_assigned_before(self):
        self.user_id_domain = json.dumps([('employee_id', '!=', False), ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', self.branch_id.id)])        

    user_id_domain = fields.Char(
        compute="get_only_not_assigned_before",
        readonly=True,
        store=False,
    )

    user_id = fields.Many2one(
        'res.users',
        string='Assigné',
        # domain="[('employee_id', '!=', False), ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', branch_id)]"
        )
    
    task_id = fields.Many2one(
        'project.task',
        string='Tâche',
        )
    
    branch_id = fields.Many2one(
        'res.branch',
        string='Territoire',
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