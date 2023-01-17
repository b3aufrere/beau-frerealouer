# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task_prepare_values(self, project):
        values = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)

        if self.order_id.opportunity_id:
            values['description'] = self.order_id.opportunity_id.description

            if self.order_id.opportunity_id.user_id:
                values['user_ids'] = [(6, 0, [self.order_id.opportunity_id.user_id.id])]
                
                stage_id = self.env['project.task.type'].search([('name', '=', 'Assigné'), ('project_ids', 'in', project.id)])
                if stage_id:
                    values['stage_id'] = stage_id.id

        return values