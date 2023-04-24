# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from datetime import date
from odoo.tools import html2plaintext, plaintext2html
from odoo.exceptions import UserError

from logging import warning as w

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_sub_task = fields.Boolean(defaul=False, compute="_compute_is_sub_task")
    is_user_readonly = fields.Boolean(defaul=False, compute="_computes_is_user_readonly")
    # territory_id = fields.Many2one('territory', string='Territoire de travail')
    branch_id = fields.Many2one('res.branch', string='Entreprise')
    date_start_expected = fields.Datetime(string="Date de début désiré")
    date_end_expected = fields.Datetime(string="Date de fin désiré")
    stage_name = fields.Char(string="Nom d'état", related="stage_id.name", store=True)
    task_cancellation_reason_id = fields.Many2one('task.cancellation.reason', string="Motif d'annulation")

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
                if task.stage_id.name == 'Planifié':
                    task.color = 4
                elif task.stage_id.name == 'En cours':
                    task.color = 10
                elif task.stage_id.name == 'Fait':
                    task.color = 1
                elif task.stage_id.name == 'Non accepté':
                    task.color = 3
                elif task.stage_id.name == 'Annulé':
                    task.color = 5
                else:
                    task.color = 0
            else:
                task.color = 0
        
            if not task.parent_id and task.helpdesk_ticket_id:
                self._compute_stage_id_of_helpdesk_ticket_id(task.helpdesk_ticket_id)
            elif task.parent_id and task.parent_id.helpdesk_ticket_id:
                self._compute_stage_id_of_helpdesk_ticket_id(task.parent_id.helpdesk_ticket_id)

    def _compute_stage_id_of_helpdesk_ticket_id(self, ticket):
        if not ticket.fsm_task_ids:
            stage_new_id = self.env.ref("helpdesk.stage_new")
            if stage_new_id:
                ticket.stage_id =  stage_new_id.id
        
        else:
            fsm_tasks_ids = ticket.fsm_task_ids.ids
            fsm_sub_tasks_ids = self.env['project.task'].sudo().search([('parent_id', 'in', fsm_tasks_ids)])
            if fsm_sub_tasks_ids:
                fsm_tasks_ids += fsm_sub_tasks_ids.ids
            
            fsm_tasks_ids = self.env['project.task'].sudo().browse(fsm_tasks_ids)
            
            # all fsm tasks are done
            stage_done_task_id = self.env.ref('bfal_workflow.project_stage_2')
            stage_cancelled_task_id = False
            stage_done_ticket_id = self.env.ref('bfal_workflow.stage_done')
            check_other_cases = True
            
            if stage_done_task_id and stage_done_ticket_id:
                nb_tasks_done = 0
                nb_task_other = 0

                for task in fsm_tasks_ids:
                    if task.stage_id.id == stage_done_task_id.id:
                        nb_tasks_done += 1
                    else:
                        if not stage_cancelled_task_id:
                            stage_cancelled_task_id = self.env.ref('bfal_workflow.project_stage_2')
                        
                        if task.stage_id.id != stage_cancelled_task_id.id:
                            nb_task_other += 1
                
                if nb_task_other == 0 and nb_tasks_done > 0:
                    ticket.stage_id = stage_done_ticket_id.id
                    check_other_cases = False
            
            if check_other_cases:
                # all fsm tasks are cancelled
                stage_cancelled_task_id = self.env.ref('bfal_workflow.project_stage_2')
                stage_cancelled_ticket_id = self.env.ref('helpdesk.stage_cancelled')
                
                if stage_cancelled_task_id and stage_cancelled_ticket_id and all(task.stage_id and task.stage_id.id == stage_cancelled_task_id.id for task in fsm_tasks_ids):
                    ticket.stage_id = stage_cancelled_ticket_id.id
                
                else:
                    # one of fsm tasks is in progress
                    stage_in_progress_task_id = self.env.ref('bfal_workflow.project_stage_1')
                    stage_in_progress_ticket_id = self.env.ref('helpdesk.stage_in_progress')
                    
                    if stage_in_progress_task_id and stage_in_progress_ticket_id and any(task.stage_id and task.stage_id.id == stage_in_progress_task_id.id for task in fsm_tasks_ids):
                        ticket.stage_id = stage_in_progress_ticket_id.id
                    
                    else:
                        # one of fsm tasks is new or planned or not accepted
                        stage_new_task_id = self.env.ref('bfal_workflow.project_stage_0')
                        stage_planned_task_id = self.env.ref('bfal_workflow.planning_project_stage_1')
                        stage_not_accepted_task_id = self.env.ref('bfal_workflow.project_stage_not_accepted')
                        stage_on_hold_ticket_id = self.env.ref('helpdesk.stage_on_hold')
                        
                        if ((stage_new_task_id and any(task.stage_id and task.stage_id.id == stage_new_task_id.id for task in fsm_tasks_ids))\
                                or (stage_planned_task_id and any(task.stage_id and task.stage_id.id == stage_planned_task_id.id for task in fsm_tasks_ids)) \
                                    or (stage_not_accepted_task_id and any(task.stage_id and task.stage_id.id == stage_not_accepted_task_id.id for task in fsm_tasks_ids))) \
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
    
    @api.depends('planned_date_begin', 'planned_date_end', 'user_ids')
    def _compute_planning_overlap(self):
        super(ProjectTask, self)._compute_planning_overlap()

        twilio_sms_accounts = self.env['twilio.sms.gateway.account'].sudo().search([('state', '=', 'confirmed')], order="id asc")
        tobe_twilio_sms_accounts = twilio_sms_accounts.filtered(lambda x: x.is_default_sms_account)
        twilio_sms_account = False
        if tobe_twilio_sms_accounts:
            twilio_sms_account = tobe_twilio_sms_accounts[0]
        elif twilio_sms_accounts:
            twilio_sms_account = twilio_sms_accounts[0]
        
        if twilio_sms_account and twilio_sms_account.is_notify_worker_abt_his_new_task and twilio_sms_account.sms_notify_worker_abt_his_new_task_template_id:
            for task in self:
                if task.id and task.user_ids and task.user_ids[0].partner_id and task.user_ids[0].partner_id.phone:
                    message = task._message_sms_with_template_twilio(
                            template=twilio_sms_account.sms_notify_worker_abt_his_new_task_template_id,
                        )
                    message = html2plaintext(message) #plaintext2html(html2plaintext(message))
                    
                    datas = {
                        "From": twilio_sms_account.account_from_mobile_number,
                        "To": (task.user_ids[0].partner_id.phone or "").replace(" ", ""),
                        "Body": message
                    }
                    twilio_sms_account.send_sms_to_recipients_from_another_src(datas)
                    task.message_post(body="SMS ENVOYÉ" + plaintext2html(html2plaintext(message)), message_type='sms')


    @api.onchange('branch_id')
    def onchange_branch_id(self):
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
                        'default_branch_id': self.branch_id.id if self.branch_id else False,
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
            stage_in_progress_id = False
            if not self.parent_id and self.project_id:
                stage_in_progress_id = self.env['project.task.type'].search([('name', '=', 'En cours'), ('project_ids', 'in', self.project_id.id)], limit=1)
            elif self.display_project_id:
                stage_in_progress_id = self.env['project.task.type'].search([('name', '=', 'En cours'), ('project_ids', 'in', self.display_project_id.id)], limit=1)
            
            if stage_in_progress_id:
                if task.stage_id and task.stage_id.id != stage_in_progress_id.id:
                    task.stage_id =  stage_in_progress_id.id
            else:
                raise UserError("Il faut ajouté une étape En cours a ce projet")

        return res 

    def action_schedule_task(self):
        for task in self:
            stage_planned_id = False
            if not self.parent_id and self.project_id:
                stage_planned_id = self.env['project.task.type'].search([('name', '=', 'Planifié'), ('project_ids', 'in', self.project_id.id)], limit=1)
            elif self.display_project_id:
                stage_planned_id = self.env['project.task.type'].search([('name', '=', 'Planifié'), ('project_ids', 'in', self.display_project_id.id)], limit=1)
            
            if stage_planned_id:
                task.stage_id = stage_planned_id.id
            else:
                raise UserError("Il faut ajouté une étape Planifié a ce projet")
    
    def action_fsm_validate(self, stop_running_timers=False):
        """ Moves Task to next stage.
            If allow billable on task, timesheet product set on project and user has privileges :
            Create SO confirmed with time and material.
        """
        Timer = self.env['timer.timer']
        tasks_running_timer_ids = Timer.search([('res_model', '=', 'project.task'), ('res_id', 'in', self.ids)])
        timesheets = self.env['account.analytic.line'].sudo().search([('task_id', 'in', self.ids)])
        timesheets_running_timer_ids = None
        if timesheets:
            timesheets_running_timer_ids = Timer.search([
                ('res_model', '=', 'account.analytic.line'),
                ('res_id', 'in', timesheets.ids)])
        if tasks_running_timer_ids or timesheets_running_timer_ids:
            if stop_running_timers:
                self._stop_all_timers_and_create_timesheets(tasks_running_timer_ids, timesheets_running_timer_ids, timesheets)
            else:
                wizard = self.env['project.task.stop.timers.wizard'].create({
                    'line_ids': [Command.create({'task_id': task.id}) for task in self],
                })
                return {
                    'name': _('Do you want to stop the running timers?'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_id': self.env.ref('industry_fsm.view_task_stop_timer_wizard_form').id,
                    'target': 'new',
                    'res_model': 'project.task.stop.timers.wizard',
                    'res_id': wizard.id,
                }

        closed_stage_by_project = {
            project.id:
                project.type_ids.filtered(lambda stage: stage.fold)[:1] or project.type_ids[-1:]
            for project in self.project_id
        }
        for task in self:
            # determine closed stage for task
            closed_stage = closed_stage_by_project.get(self.project_id.id)
            values = {'fsm_done': True}
            if closed_stage:
                values['stage_id'] = closed_stage.id

            task.write(values)
        
        billable_tasks = self.filtered(lambda task: task.allow_billable and (task.allow_timesheets or task.allow_material))
        timesheets_read_group = self.env['account.analytic.line'].sudo().read_group([('task_id', 'in', billable_tasks.ids), ('project_id', '!=', False)], ['task_id', 'id'], ['task_id'])
        timesheet_count_by_task_dict = {timesheet['task_id'][0]: timesheet['task_id_count'] for timesheet in timesheets_read_group}
        for task in billable_tasks:
            if task.timesheet_product_id and task.timesheet_product_id.lst_price > 0 :
                timesheet_count = timesheet_count_by_task_dict.get(task.id)
                if not task.sale_order_id and not timesheet_count:  # Prevent creating/confirming a SO if there are no products and timesheets
                    continue
                task._fsm_ensure_sale_order()
                if task.allow_timesheets:
                    task._fsm_create_sale_order_line()
                if task.sudo().sale_order_id.state in ['draft', 'sent']:
                    task.sudo().sale_order_id.action_confirm()
            billable_tasks._prepare_materials_delivery()

        return True
    
    def action_reassign_task(self):
        # for task in self:
        #     new_stage_id = False
        #     if not self.parent_id and self.project_id:
        #         new_stage_id = self.env['project.task.type'].search([('name', '=', 'Nouveau'), ('project_ids', 'in', self.project_id.id)], limit=1)
        #     elif self.display_project_id:
        #         new_stage_id = self.env['project.task.type'].search([('name', '=', 'Nouveau'), ('project_ids', 'in', self.display_project_id.id)], limit=1)
            
        #     if new_stage_id:
        #         task.stage_id = new_stage_id.id
        #     else:
        #         raise UserError("Il faut ajouté une étape Nouveau a ce projet")
        user_ids = []

        for tah in self.env['task.assignment.history'].sudo().search([('task_id', '=', self.id)]):
            user_ids +=  [user.id for user in tah.user_ids]

        domain = [('employee_id', '!=', False), ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', self.branch_id.id)]
        if user_ids:
            domain.append(('id', 'not in', user_ids))
        
        user_ids = self.env['res.users'].sudo().search(domain)     

        return {
            'name':_("Réassignation"),
            'view_mode': 'form',
            'view_id': self.env.ref("bfal_workflow.view_task_reassignment_form").id,
            'res_model': 'task.reassignment',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_branch_id': self.branch_id.id,
                'default_task_id': self.id,
                'default_user_ids': [(6, 0, user_ids.ids)] if user_ids else []
            }
        }
    
    def action_cancel_task(self):  
        return {
            'name':_("Annulation de tâche"),
            'view_mode': 'form',
            'view_id': self.env.ref("bfal_workflow.view_task_cancellation_wiz_form").id,
            'res_model': 'task.cancellation.wiz',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
            }
        }