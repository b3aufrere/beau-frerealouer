# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_sub_task = fields.Boolean(defaul=False, compute="_compute_is_sub_task")
    is_user_readonly = fields.Boolean(defaul=False, compute="_computes_is_user_readonly")
    territory_id = fields.Many2one('territory', string='Territoire de travail')
    date_start_expected = fields.Datetime(string="Date de début désiré")
    date_end_expected = fields.Datetime(string="Date de fin désiré")

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        """
            colors :
                0  : none 
                1  : red
                10 : green
                2  : Orange
                3  : Yellow
                4  : Blue
                5  : Dark Purple
        """
        for task in self:
            if task.stage_id:
                if task.stage_id.name == "Planned":
                    task.color = 4
                elif task.stage_id.name == "In Progress":
                    task.color = 10
                elif task.stage_id.name == "Done":
                    task.color = 1
                elif task.stage_id.name == "Not accepted":
                    task.color = 3
                elif task.stage_id.name == "Canceled":
                    task.color = 5


    @api.depends('parent_id')
    def _compute_is_sub_task(self):
        for task in self:
            task.is_sub_task = True if task.parent_id else False
    
    @api.depends('user_ids')
    def _computes_is_user_readonly(self):
        for task in self:
            task.is_user_readonly = not self.env.user.sudo().has_group('industry_fsm.group_fsm_manager')

    @api.onchange('territory_id')
    def onchange_territory_id(self):
        for task in self:
            if not isinstance(self.id, models.NewId) or self._origin:
                task.user_ids = False

    def create_sub_task(self):
        view_id = self.env.ref("project.view_task_form2")

        if view_id:
            return {
                    'name': _("My Tasks"),
                    'type': 'ir.actions.act_window',
                    'res_model': 'project.task',
                    'view_mode': 'form',
                    'view_id': view_id.id,
                    'context': {
                        'default_user_ids': [(4, [user_id.id]) for user_id in self.user_ids] if self.user_ids else False,
                        'default_sale_order_id': self.sale_order_id.id if self.sale_order_id else False,
                        'default_partner_id': self.partner_id.id if self.partner_id else False,
                        'default_company_id': self.company_id.id if self.company_id else False,
                        'default_territory_id': self.territory_id.id if self.territory_id else False,
                        'default_parent_id': self.parent_id.id if self.parent_id else self.id,
                        'default_is_fsm': True,
                        'fsm_mode': True,            
                        'search_default_my_tasks': True, 
                        'search_default_tasks_not_planned': True,         
                        'search_default_planned_future': True,            
                        'search_default_planned_today': True,            
                        'default_scale': 'day',          
                    },
                    'target': 'current',
                }