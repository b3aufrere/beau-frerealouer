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
        view_id = self.env.ref("bfal_workflow.mail_activity_view_task_not_accepted")

        if view_id:
            return {
                    'name': "Non Acceptation",
                    'type': 'ir.actions.act_window',
                    'res_model': 'mail.activity',
                    'view_mode': 'form',
                    'view_id': view_id.id,
                    'context': {
                        'default_activity_type_id': self.env.ref("bfal_workflow.activity_type_task_not_accepted").id,
                        'default_date_deadline': date.today(),
                        'default_user_id': self.create_uid.id,
                        'default_res_model_id': self.env.ref("project.model_project_task").id,
                        'default_res_id': self.id,
                        'is_from_task': True     
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
        
            if task.helpdesk_ticket_id:
                self._compute_stage_id_of_helpdesk_ticket_id(task.helpdesk_ticket_id)

    def _compute_stage_id_of_helpdesk_ticket_id(self, ticket):
        if not ticket.fsm_task_ids:
            stage_new_id = self.env.ref("helpdesk.stage_new")
            if stage_new_id:
                ticket.stage_id =  stage_new_id.id
        
        else:
            # all fsm tasks are done
            stage_done_task_id = self.env.ref('project.project_stage_2')
            stage_cancelled_task_id = False
            stage_done_ticket_id = self.env.ref('helpdesk.stage_done')
            check_other_cases = True
            
            if stage_done_task_id and stage_done_ticket_id:
                nb_tasks_done = 0
                nb_task_other = 0

                for task in ticket.fsm_task_ids:
                    if task.stage_id.id == stage_done_task_id.id:
                        nb_tasks_done += 1
                    else:
                        if not stage_cancelled_task_id:
                            stage_cancelled_task_id = self.env.ref('project.project_stage_3')
                        elif task.stage_id.id != stage_cancelled_task_id.id:
                            nb_task_other += 1
                
                if nb_task_other == 0 and nb_tasks_done > 0:
                    ticket.stage_id = stage_done_ticket_id.id
                    check_other_cases = False
            
            if check_other_cases:
                # all fsm tasks are cancelled
                stage_cancelled_task_id = self.env.ref('project.project_stage_3')
                stage_cancelled_ticket_id = self.env.ref('helpdesk.stage_cancelled')
                
                if stage_cancelled_task_id and stage_cancelled_ticket_id and all(task.stage_id and task.stage_id.id == stage_cancelled_task_id.id for task in ticket.fsm_task_ids):
                    ticket.stage_id = stage_cancelled_ticket_id.id
                
                else:
                    # one of fsm tasks is in progress
                    stage_in_progress_task_id = self.env.ref('project.project_stage_1')
                    stage_in_progress_ticket_id = self.env.ref('helpdesk.stage_in_progress')
                    
                    if stage_in_progress_task_id and stage_in_progress_ticket_id and any(task.stage_id and task.stage_id.id == stage_in_progress_task_id.id for task in ticket.fsm_task_ids):
                        ticket.stage_id = stage_in_progress_ticket_id.id
                    
                    else:
                        # one of fsm tasks is new or planned or not accepted
                        stage_new_task_id = self.env.ref('project.project_stage_0')
                        stage_planned_task_id = self.env.ref('industry_fsm.planning_project_stage_1')
                        stage_not_accepted_task_id = self.env.ref('bfal_workflow.project_stage_not_accepted')
                        stage_on_hold_ticket_id = self.env.ref('helpdesk.stage_on_hold')
                        
                        if ((stage_new_task_id and any(task.stage_id and task.stage_id.id == stage_new_task_id.id for task in ticket.fsm_task_ids))\
                                or (stage_planned_task_id and any(task.stage_id and task.stage_id.id == stage_planned_task_id.id for task in ticket.fsm_task_ids)) \
                                    or (stage_not_accepted_task_id and any(task.stage_id and task.stage_id.id == stage_not_accepted_task_id.id for task in ticket.fsm_task_ids))) \
                                        and stage_on_hold_ticket_id:
                            ticket.stage_id = stage_on_hold_ticket_id.id


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

    def action_timer_start(self):
        res = super(ProjectTask, self).action_timer_start()
        
        for task in self:
            stage_in_progress_id = self.env.ref("project.project_stage_1")
            if stage_in_progress_id and task.stage_id and task.stage_id.id != stage_in_progress_id.id:
                task.stage_id =  stage_in_progress_id.id

        return res 

    def action_schedule_task(self):
        for task in self:
            stage_planned_id = self.env.ref("industry_fsm.planning_project_stage_1")
            if stage_planned_id:
                task.stage_id =  stage_planned_id.id