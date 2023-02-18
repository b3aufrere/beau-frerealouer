# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)

class task_wizard(models.Model):
    _name= 'task.website.wizard'
    _description = "Task Wizard"

    name = fields.Char('Task Name',readonly=False)
    project_id = fields.Many2one('project.project','Project',readonly=False)
    user_id = fields.Many2one('res.users','Assigned To',readonly=False)
    planned_hours = fields.Float('Planned Hours',readonly=False)
    description = fields.Html('Description',readonly=False)
    tag_ids = fields.Many2many('project.tags',readonly=False)
    deadline_date = fields.Date('Deadline Date',readonly=False)

    @api.model 
    def default_get(self, flds): 
        result = super(task_wizard, self).default_get(flds)
        suport_ticket_id = self.env['support.ticket'].browse(self._context.get('active_id'))
        result['name'] = suport_ticket_id.name
        result['description'] = suport_ticket_id.description
        result['deadline_date'] = datetime.now()
        if suport_ticket_id.project_id:
            result['project_id'] = suport_ticket_id.project_id.id
        if suport_ticket_id.user_id:
            result['user_id'] = suport_ticket_id.user_id.id
        return result
    
    def create_task(self):
        support_ticket_id = self.env['support.ticket'].browse(self._context.get('active_id'))
        project_task_obj  = self.env['project.task']
        list_of_tag = []
        for tag in self.tag_ids:
            list_of_tag.append(tag.id)
        vals = {
                'name' : self.name,
                'project_id' : self.project_id.id,
                'user_ids': [(6, 0, self.user_id.ids)],
                'tag_ids' : [(6,0,list_of_tag)],
                'ticket_id' : support_ticket_id.id,
                'description' : self.description,
                'planned_hours' : self.planned_hours,
                'date_deadline' : self.deadline_date
                }

        project_task = project_task_obj.create(vals)
        return project_task

    
