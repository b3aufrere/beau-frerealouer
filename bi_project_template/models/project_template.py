# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api , _
from odoo.exceptions import UserError

class project_project(models.Model):

    _inherit = "project.project"

    @api.model
    def default_get(self, flds):

        stage_type_obj = self.env['template.task']
        state_new_id = stage_type_obj.search([('name', '=', 'New')], limit=1)
        if state_new_id:
            state_new_id.write({'sequence':1, 'task_check':True})
        else:
            state_new_id = stage_type_obj.create({'name':'New', 'sequence':1, 'task_check':True})
        state_in_progress_id = stage_type_obj.search([('name', '=', 'In Progress')], limit=1)
        if state_in_progress_id:
            state_in_progress_id.write({'sequence':2, 'task_check':True})
        else:
            progress_id = stage_type_obj.create({'name':'In Progress', 'sequence':2, 'task_check':True})
        state_cancel_id = stage_type_obj.search([('name', '=', 'Canceled')], limit=1)
        if state_cancel_id:
            state_cancel_id.write({'sequence':3, 'task_check':True})
        else:
            cancel_id = stage_type_obj.create({'name':'Canceled', 'sequence':3, 'task_check':True})
        state_pending_id = stage_type_obj.search([('name', '=', 'Pending')], limit=1)
        if state_pending_id:
            state_pending_id.write({'sequence':4, 'task_check':True})
        else:
            pending_id = stage_type_obj.create({'name':'Pending', 'sequence':4, 'task_check':True})
        state_closed_id = stage_type_obj.search([('name', '=', 'Closed')], limit=1)
        if state_closed_id:
            state_closed_id.write({'sequence':5, 'task_check':True})
        else:
            closed_id = stage_type_obj.create({'name':'Closed', 'sequence':4, 'task_check':True})
        stage_list = []
        result = super(project_project, self).default_get(flds)
        for i in state_new_id:
            result['template_task_id'] = i.id
        return result


    def count_sequence(self):
        for a in self:
            stage_type_obj = a.env['template.task']
            state_in_progress_id = stage_type_obj.search([('name', '=', 'In Progress')], limit=1)
            state_template_id = stage_type_obj.search([('name', '=', 'Template')], limit=1)
            state_new_id = stage_type_obj.search([('name', '=', 'New')], limit=1)
            if a.template_task_id.id == int(state_new_id):
                a.sequence_state = 1
            elif a.template_task_id.id == int(state_in_progress_id):
                a.sequence_state = 2
            else:
                a.sequence_state = 3

    def set_template(self):
        for i in self:
            stage_type_obj = self.env['template.task']
            state_template_id = stage_type_obj.search([('name', '=', 'Template')], limit=1)
            state_new_id = stage_type_obj.search([('name', '=', 'New')], limit=1)
            if state_template_id:
                state_template_id.write({'sequence':1, 'task_check':True})
                state_new_id.update({'sequence':2, 'task_check':True})
                i.update({'template_task_id':state_template_id.id, 'sequence_state':3})
            else:
                template_id = stage_type_obj.create({'name':'Template', 'sequence':1, 'task_check':True})
                template_id.write({'sequence':1, 'task_check':True})
                state_new_id.write({'sequence':2, 'task_check':True})
                i.write({'template_task_id':template_id.id, 'sequence_state':3})
            state_template_id.write({'task_check':False})

    def new_project(self):
        for i in self:
            stage_type_obj = self.env['template.task']
            state_template_id = stage_type_obj.search([('name', '=', 'Template')], limit=1)
            state_new_id = stage_type_obj.search([('name', '=', 'New')], limit=1)
            test = i.name
            template_copy_id = self.env['project.project'].search([('project_project_id', '=', i.id),('is_project_template','=',False)])
            if not template_copy_id:
                project_id = i.with_context(project_template=True).copy({'project_project_id':i.id,'is_project_template': False})
                if state_template_id:
                    state_new_id = stage_type_obj.search([('name', '=', 'New')], limit=1)
                    project_id.write({'template_task_id':state_new_id.id, 'sequence_state':1,})
            return

    def copy(self, default=None, context=None):
        project = super(project_project, self).copy(default)
        stage_type_obj = self.env['template.task']
        state_new_id = stage_type_obj.search([('name', '=', 'New')], limit=1)
        if self.env.user.has_group('project.group_project_stages'):
            if self.env.context.get('default_is_project_template', True) and not self.env.context.get('project_template'):
                project.update({'template_task_id':state_new_id, 'sequence_state':1,'is_project_template':True})
        return project 


    def reset_project(self):
        for i in self:
            stage_type_obj = self.env['project.task.type']
            state_new_id = stage_type_obj.search([('name', '=', 'New')], limit=1)
            if state_new_id:
                i.write({'template_task_id':state_new_id.id, 'sequence_state':1})
            return 

    def set_progress(self):
        for i in self:
            stage_type_obj = self.env['template.task']
            state_progress_id = stage_type_obj.search([('name', '=', 'In Progress')], limit=1)
            if state_progress_id:
                i.write({'template_task_id':state_progress_id.id, 'sequence_state':2})
            return 

    template_task_id = fields.Many2one('template.task', string="state")
    sequence_state = fields.Integer(compute="count_sequence", string="State Check")
    project_project_id = fields.Many2one('project.project',string ="Project Template")
    is_project_template = fields.Boolean('Is Project Template')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
