# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project_task'

    def create_sub_task(self):
        action = self.env["ir.actions.actions"]._for_xml_id("industry_fsm.project_task_action_fsm")
        if action:
            action['context'] = {
                'default_user_ids': [(4, [user_id.id]) for user_id in self.user_ids] if self.user_ids else False,
                'default_sale_order_id': self.sale_order_id.id if self.sale_order_id else False,
                'default_project_id': self.project_id.id if self.project_id else False,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
                'default_company_id': self.company_id.id if self.company_id else False,
                'default_parent_id': self.id,                     
            }
            
            return action