# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.osv import osv
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning


class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    warning_child_task = fields.Many2one('project.task.type', 'Prevent stage to change untill all task on same stage')

    @api.model
    def get_values(self):
        res = super(res_config_settings,self).get_values()
        warning_child_task = self.env['ir.config_parameter'].sudo().get_param('bi_subtask.warning_child_task')
        if warning_child_task:
            res.update(
                warning_child_task = int(warning_child_task),
                
                )
        return res

    def set_values(self):
        res=super(res_config_settings,self).set_values()
        warning_child_task = self.env['ir.config_parameter'].sudo().set_param('bi_subtask.warning_child_task', self.warning_child_task.id)
        return res


class subtask_wizard(models.Model):
    _name = 'subtask.wizard'
    _description = "Subtask Wizard"

    subtask_lines = fields.One2many('project.task', 'wiz_id', string="Task Line")

    def create_subtask(self):
        list_of_stage = []
        project_task_id = self.env['project.task'].browse(self._context.get('active_id'))
        for stage in project_task_id.project_id.type_ids:
            stage_ids = self.env['project.task.type'].search([('id', '=', stage.id)])
            list_of_stage.append(stage_ids.id)
        for task in self.subtask_lines:
            task.task_parent_id = self._context.get('active_id')
            task.description = task.des
            task.is_subtask = True
            task.project_id = project_task_id.project_id.id
            if list_of_stage:
                task.stage_id = list_of_stage[0]
            
        return True


class ProjectTask(models.Model):
    _inherit = "project.task"

    wiz_id = fields.Many2one('subtask.wizard', string="Wiz Parent Id")
    task_parent_id = fields.Many2one('project.task', string="Parent Id")
    subtask_ids = fields.One2many('project.task', 'task_parent_id', string="Subtask")
    des = fields.Char('Task Description')
    is_subtask = fields.Boolean('Is a subtask')

    @api.onchange('parent_id')
    def button_disable(self):
        if self.parent_id:
            self.is_subtask = True
            self.task_parent_id = self.parent_id.id
            self.project_id = self.parent_id.project_id
        else:
            self.is_subtask = False
            self.task_parent_id = self.id
            self.project_id = False

    def write(self, vals):
        if vals.get('stage_id'):
            task_type_search = self.env['ir.config_parameter'].sudo().get_param('bi_subtask.warning_child_task')
        
            if task_type_search:

                if vals.get('stage_id') == int(task_type_search):
                    for task in self.subtask_ids:
                        if task.stage_id.id != int(task_type_search):
                            raise UserError("You can not close parent task until all child tasks are closed.")
        return super(ProjectTask, self).write(vals)

    def _compute_subtask_count(self):
        for task in self:
            task_ids = self.env['project.task'].search([('task_parent_id', '=', task.id)])
            task.subtask_count = len(task_ids)
            self.parent_id = task.task_parent_id
