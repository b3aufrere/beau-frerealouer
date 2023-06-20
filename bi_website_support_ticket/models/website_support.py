# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)
      
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    ticket_id = fields.Many2one('support.ticket','Support Ticket')
    
class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    ticket_id = fields.Many2one('support.ticket',
        string='Support Ticket',track_visibility='onchange',change_default=True)
        
class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    
    ticket_stage = fields.Boolean("Support Ticket Stage")

class account_invoice(models.Model):
    _inherit='account.move'

    invoice_support_ticket_id  =  fields.Many2one('support.ticket', 'Support Ticket')
    
class ir_attachment(models.Model):
    _inherit='ir.attachment'

    support_ticket_id  =  fields.Many2one('support.ticket', 'Support Ticket')

class Website(models.Model):

    _inherit = "website"
    
    def get_website_config(self):
        config_ids = self.env["ir.config_parameter"].sudo().get_param('bi_website_support_ticket.support_ticket_visible') 
        return str(config_ids) 
    
    def get_support_team_list(self):            
        support_team_ids=self.env['support.team'].sudo().search([])
        return support_team_ids
        
    def get_ticket_details(self):            
        partner_brw = self.env['res.users'].browse(self._uid)
        ticket_ids = self.env['support.ticket'].sudo().search(['|',('partner_id','=',partner_brw.partner_id.id),('user_id','=',partner_brw.id)])
        return ticket_ids
        
    def get_ticket_type(self):            
        ticket_type_ids = self.env['support.ticket.type'].sudo().search([])
        return ticket_type_ids     

    def get_team_details(self):
        support_team = self.env['support.team'].sudo().search([])
        team_list = []
        for team in support_team :
            team_list.append(team)
        return team_list 

    def get_partner_details(self):
        partner_id = self.env['res.partner'].sudo().search([])
        partner_list = []
        for partner in partner_id :
            partner_list.append(partner)
        return partner_list

    def get_category_details(self):
        ticket_type_ids = self.env['support.ticket.type'].sudo().search([])
        category_list = []
        for category in ticket_type_ids :
            category_list.append(category)
        return category_list

    def get_project_details(self):
        project_id = self.env['project.project'].sudo().search([('privacy_visibility','=','portal'),('favorite_user_ids', 'in', [self.env.user.id])])
        project_list = []
        for project in project_id :
            project_list.append(project)
        return project_list

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
