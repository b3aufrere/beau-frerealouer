# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.tools.translate import _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import api, fields, models, _
import logging
from odoo.osv import  osv
from odoo import SUPERUSER_ID

from logging import warning as w

class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"

    def task_count(self):
        task_obj = self.env['project.task']
        self.task_number = task_obj.search_count([('lead_id', 'in', [a.id for a in self])])

    task_number = fields.Integer(compute='task_count', string='Tasks')
    
class crm_task_wizard(models.TransientModel):
    _name = 'crm.task.wizard'
    _description = "CRM Task Wizard"
    
    
    def get_name(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['crm.lead'].browse(active_id)
        name = crm_brw.name
        return name
    
    
    project_id = fields.Many2one('project.project','Projet')
    # dead_line = fields.Date('Deadline')
    planned_date_begin = fields.Datetime(string="Date de début")
    planned_date_end = fields.Datetime(string="Date de fin")
    name = fields.Char('Nom de la tâche',default = get_name)
    # user_ids = fields.Many2many('res.users',string='Assignés')
    # user_ids = fields.Many2many('res.users', relation='project_task_assignee_rel', column1='task_id', column2='user_id',
    #     string='Assignees', default=lambda self: self.env.user)

    def create_task(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['crm.lead'].browse(active_id)
        user = []
        
        # for users in self.user_ids:
        #     user.append(users.id)
        
        vals = {
            'name': self.name,
            'project_id':self.project_id.id or False,
            # 'user_ids': user or False,
            # 'date_deadline':  self.dead_line or False,
            'planned_date_begin':  self.planned_date_begin,
            'planned_date_end':  self.planned_date_end,
            'partner_id': crm_brw.partner_id.id or False,
            'lead_id': crm_brw.id or False,
            'branch_id': crm_brw.branch_id.id or False,
            'user_ids': [(6, 0, [crm_brw.user_id.id])] if crm_brw.user_id else False
        }
        
        self.env['project.task'].create(vals)
        
class project_Task(models.Model):
    _inherit='project.task'
    
    lead_id =  fields.Many2one('crm.lead', 'Opportunity')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
