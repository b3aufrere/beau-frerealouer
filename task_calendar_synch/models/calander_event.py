# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    custom_task_id = fields.Many2one(
        'project.task',
        string="Task",
    )
    custom_project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

#    @api.multi #odoo13
    # def unlink(self):
    # def unlink(self, can_be_deleted=True): #odoo13 27/02/2020
    def unlink(self): #odoo13 27/02/2020
        if not self._context.get('from_task',False):
            for line in self:
                if line.custom_task_id:
                    raise UserError(_('You can not delete meeting which is linked with task.'))
        # return super(CalendarEvent, self).unlink(can_be_deleted)
        return super(CalendarEvent, self).unlink()

#    @api.multi #odoo13
    def action_open_task(self):
        self.ensure_one()
        action = self.env.ref('project.action_view_task').sudo().read()[0]
        action['domain'] = [('custom_event_id', '=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
