# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json

from logging import warning as w

class TaskReassignment(models.Model):
    _name = 'task.reassignment'
    _description = 'Réassignation de tâche'

    def get_only_not_assigned_before(self):
        w(">>> get_only_not_assigned_before 1")
        w(f"branch_id >>> {self.branch_id}")
        
        self.user_ids = False
        user_ids = self.env['res.users'].sudo().search([('employee_id', '!=', False), ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', self.branch_id.id)])     
        
        w(f"user_ids >>> {user_ids}")
        if user_ids:
            self.user_ids = [(6, 0, user_ids.ids)]
            
    user_ids = fields.Many2many('res.users', compute="get_only_not_assigned_before")

    user_id = fields.Many2one(
        'res.users',
        string='Assigné',
        # domain="[('employee_id', '!=', False), ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', branch_id)]"
        domain="[('id', 'in', user_ids)]"
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