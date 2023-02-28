# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    sh_project_id = fields.Many2one('project.project', 'Project')
    sh_task_id = fields.Many2one('project.task', 'Task')
