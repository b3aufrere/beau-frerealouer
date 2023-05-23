# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext


class ProjectTask(models.Model):
    _inherit = "project.task"

    custom_event_id = fields.Many2one(
        'calendar.event',
        string="Meeting"
    )
    custom_location = fields.Char(
        string='Meeting Location',
    )
    custom_privacy = fields.Selection([
        ('public', 'Everyone'), 
        ('private', 'Only me'), 
        ('confidential', 'Only internal users')], 
        string = 'Privacy', 
        default='public',
    )
    custom_show_as = fields.Selection([
        ('free', 'Free'), 
        ('busy', 'Busy')], 
        string ='Show Time as',
        default='busy'
    )
    custom_partner_ids = fields.Many2many(
        'res.partner',
        string='Meeting Attendees'
    )
    custom_planned_hours = fields.Float(
        string="Meeting Duration", 
    )

    @api.model
    def create(self, vals):
        #print("vals:---------------",vals)
        result = super(ProjectTask, self).create(vals)
        lines = []
        for rec in result.custom_partner_ids:
            lines.append((4,rec.id))
        for user in result.user_ids:
            lines.append((4,user.partner_id.id))
        # if result.activity_user_id:
        #     lines.append((4,result.activity_user_id.partner_id.id))
        # if vals.get('date_assign'):
        if vals.get('planned_date_begin') and vals.get('planned_date_end'):
            meeting = self.env['calendar.event'].create({
              'name':vals['name'],
              # 'start':vals.get('date_start') or vals.get('date_assign'), # while duplicating task not pass date_start
              # 'stop': vals.get('date_start') or vals.get('date_assign'), # while duplicating task not pass date_start
              'start': vals.get('planned_date_begin'), #odoo13 ('date_start' field remove in odoo13.)
              'stop': vals.get('planned_date_end'),
              'custom_task_id':result.id,
              'partner_ids':lines,
              # 'duration':vals['custom_planned_hours'],
              'duration':vals.get('custom_planned_hours', 0.0),
              'user_id':self.env.user.id,
              'custom_project_id':result.project_id.id,
              'description': html2plaintext(vals.get('description', '')),
              'location':vals.get('custom_location'),
              'privacy': vals.get('custom_privacy') or 'public',
              'show_as': vals.get('custom_show_as') or 'busy',
              'partner_id' : self.env.user.partner_id.id,
              })
            result.write({'custom_event_id':meeting.id})
        return result


#    @api.multi #odoo13
    def write(self, vals):
        res = super(ProjectTask,self).write(vals)
        event_data = {}
        #odoo13 ('date_start' field remove in odoo13.)
        #---------------------------------------------
        # if vals.get('date_start'):
        #     start = {
        #         'start':vals['date_start'],
        #         'stop':vals['date_start'],
        #     }
        #---------------------------------------------
        # if vals.get('date_assign'):
        if vals.get('planned_date_begin') and vals.get('planned_date_end'):
            start = {
                'start':vals['planned_date_begin'],
                'stop':vals['planned_date_end'],
            }
            event_data.update(start)
        if vals.get('custom_location'):
            newc_location = {
                'location':vals['custom_location'],
            }
            event_data.update(newc_location)
        if vals.get('name'):
            title = {
                'name':vals['name'],
            }
            event_data.update(title)
        if vals.get('custom_planned_hours'):
            duration_hour = {
                'duration':vals['custom_planned_hours'],
            }
            event_data.update(duration_hour)
        if vals.get('custom_privacy'):
            privacy = {
                'privacy':vals['custom_privacy'],
            }
            event_data.update(privacy)
        if vals.get('custom_show_as'):
            show = {
                'show_as':vals['custom_show_as'],
            }
            event_data.update(show)
        if vals.get('project_id'):
            project = {
                'custom_project_id':vals['project_id'],
            }
            event_data.update(project)
        for task in self:
            if task.custom_event_id:
                task.custom_event_id.write(event_data)
        return res

#    @api.multi #odoo13
    def unlink(self):
        for task in self:
            task.custom_event_id.with_context(from_task=True).unlink()
        return super(ProjectTask, self).unlink() 


#    @api.multi #odoo13
    def action_open_event(self):
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').sudo().read()[0]
        action['domain'] = [('custom_task_id', '=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
