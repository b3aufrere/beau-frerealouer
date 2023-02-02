# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_sub_task = fields.Boolean(defaul=False, compute="_compute_is_sub_task")
    is_user_readonly = fields.Boolean(defaul=False, compute="_computes_is_user_readonly")
    territory_id = fields.Many2one('territory', string='Territoire de travail')
    date_start_expected = fields.Datetime(string="Date de début désiré")
    date_end_expected = fields.Datetime(string="Date de fin désiré")

    def action_no_accept_task(self):
        self.env['mail.activity'].sudo().create({
            'summary': "J ai pas de temps, merci",
            'activity_type_id': self.env.ref("bfal_workflow.activity_type_task_not_accepted"),
            'date_deadline': date.today(),
            'user_id': self.create_uid.id,
            'res_model_id': self.env.ref("mail.model_mail_activity").id,
            'res_id': self.id 
        })
        return True
        view_id = self.env.ref("bfal_workflow.mail_activity_view_task_not_accepted")

        if view_id:
            return {
                    'name': "Non Acceptation",
                    'type': 'ir.actions.act_window',
                    'res_model': 'mail.activity',
                    'view_mode': 'form',
                    'view_id': view_id.id,
                    'context': {
                        'default_activity_type_id': self.env.ref("bfal_workflow.activity_type_task_not_accepted"),
                        'default_date_deadline': date.today(),
                        'default_user_id': self.create_uid.id,
                        'default_res_model_id': self.env.ref("mail.model_mail_activity").id,
                        'default_res_id': self.id     
                    },
                    'target': 'new',
                }

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
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
        super(ProjectTask, self)._compute_kanban_state_label()

        for task in self:
            if task.stage_id:
                if task.stage_id.id == self.env.ref("industry_fsm.planning_project_stage_1").id:
                    task.color = 4
                elif task.stage_id.id == self.env.ref("project.project_stage_1").id:
                    task.color = 10
                elif task.stage_id.id == self.env.ref("project.project_stage_2").id:
                    task.color = 1
                elif task.stage_id.id == self.env.ref("bfal_workflow.project_stage_not_accepted").id:
                    task.color = 3
                elif task.stage_id.id == self.env.ref("project.project_stage_3").id:
                    task.color = 5
                else:
                    task.color = 0
            else:
                task.color = 0


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