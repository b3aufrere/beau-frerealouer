# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import _, api, models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sh_expense_count = fields.Integer('Expense', compute="_compute_task_expense_count")

    def create_expense(self):
        vals = {
            'default_name': self.name,
            'default_sh_project_id': self.project_id.id,
            'default_sh_task_id': self.id
        }
        return {
            'name': _('Create Hr Expense'),
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
            'res_model': 'hr.expense',
            'type': 'ir.actions.act_window',
            'context': vals,
        }

    @api.depends('sh_expense_count')
    def _compute_task_expense_count(self):
        for rec in self:
            expense = self.env['hr.expense'].search(
                [('sh_task_id', '=', rec.id)])
            if expense:
                rec.sh_expense_count = len(expense.ids)
            else:
                rec.sh_expense_count = 0

    def action_task_expense(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "hr.expense",
            "domain": [('sh_task_id', '=', self.id)],
            "context": {"create": False},
            "name": "Expenses",
            'view_mode': 'tree,form',
        }
        return result
