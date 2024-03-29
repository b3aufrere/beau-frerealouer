# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

from logging import warning as w

class Reassignment(models.TransientModel):
    _name = 'reassignment'
    _description = 'Réassignation'
            
    user_ids = fields.Many2many('res.users')

    user_id = fields.Many2one(
        'res.users',
        string='Assigné',
        # domain="[('employee_id', '!=', False), ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', branch_id)]"
        # domain="[('id', 'in', user_ids)]"
    )
    
    task_id = fields.Many2one(
        'project.task',
        string='Tâche',
        )
    
    order_id = fields.Many2one(
        'sale.order',
        string='Soumission',
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
    
    def action_reassign_order(self):
        self.order_id.state = 'draft'
        self.order_id.user_id = self.user_id.id