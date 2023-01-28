# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

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
                        'default_project_id': self.project_id.id if self.project_id else False,
                        'default_partner_id': self.partner_id.id if self.partner_id else False,
                        'default_company_id': self.company_id.id if self.company_id else False,
                        'default_parent_id': self.id,
                        'default_is_fsm': True,
                        'fsm_mode': True,            
                        'search_default_my_tasks': True,            
                        'search_default_planned_future': True,            
                        'search_default_planned_today': True,            
                        'default_scale': 'day',          
                    },
                    'target': 'current',
                }