# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

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
        super(HelpdeskTicket, self)._compute_kanban_state_label()

        for ticket in self:
            if ticket.stage_id:
                if ticket.stage_id.id == self.env.ref("helpdesk.stage_on_hold").id:
                    ticket.color = 4
                elif ticket.stage_id.id == self.env.ref("helpdesk.stage_in_progress").id:
                    ticket.color = 10
                elif ticket.stage_id.id == self.env.ref("helpdesk.stage_done").id \
                        or ticket.stage_id.id == self.env.ref("helpdesk.stage_solved").id:
                    ticket.color = 1
                elif ticket.stage_id.id == self.env.ref("helpdesk.stage_cancelled").id:
                    ticket.color = 5
                else:
                    ticket.color = 0
            else:
                ticket.color = 0
    
    @api.depends('fsm_task_ids.stage_id')
    def _compute_stage_id_depends_on_fsm_tasks_stage_id(self):
        for ticket in self:
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