# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task_prepare_values(self, project):
        values = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)

        if self.order_id.opportunity_id:
            values['description'] = self.order_id.internal_note
            values['branch_id'] = self.order_id.branch_id.id if self.order_id.branch_id else False
            values['lead_id'] = self.order_id.opportunity_id.id if self.order_id.opportunity_id else False

            if self.order_id.opportunity_id.user_id:
                values['user_ids'] = [(6, 0, [self.order_id.opportunity_id.user_id.id])]
                
                # stage_id = self.env['project.task.type'].search([('name', '=', 'Assigné'), ('project_ids', 'in', project.id)])
                # if stage_id:
                #     values['stage_id'] = stage_id.id
        
        elif self.order_id.user_id:
            values['branch_id'] = self.order_id.branch_id.id if self.order_id.branch_id else False
            values['user_ids'] = [(6, 0, [self.order_id.user_id.id])]
            values['description'] = self.order_id.internal_note

        return values
    