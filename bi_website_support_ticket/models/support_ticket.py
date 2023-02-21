# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _,exceptions
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from collections import defaultdict

import logging
_logger = logging.getLogger(__name__)


class support_ticket(models.Model):

    _name = "support.ticket" 
    _inherit = ['portal.mixin', 'mail.thread', 'utm.mixin', 'rating.mixin', 'mail.activity.mixin']
    _order = 'date_create desc, id desc'
    _description = "Support Ticket"     
    
    def set_to_close(self):
        stage_obj = self.env['support.stage'].search([('name','=','Closed')])
        a = self.write({'stage_id':stage_obj.id,'is_ticket_closed':True,'date_close':datetime.now()})
        return a
        
    def set_to_reset(self):
        stage_obj = self.env['support.stage'].search([('name','=','New')])
        a = self.write({'stage_id':stage_obj.id,'is_ticket_closed':False})
        return a        
        
    @api.model 
    def default_get(self, flds): 
        result = super(support_ticket, self).default_get(flds)
        stage_nxt1 = self.env['ir.model.data']._xmlid_to_res_id('bi_website_support_ticket.support_stage') 
        result['stage_id'] = stage_nxt1
        result['is_ticket_closed'] = False
        return result
        
    def stage_find(self):
        return self.env['support.stage'].search([], limit=1).id
            
    def _get_attachment_count(self):
        for ticket in self:
            attachment_ids = self.env['ir.attachment'].search([('support_ticket_id','=',ticket.id)])
            ticket.attachment_count = len(attachment_ids)
        
    def attachment_on_support_ticket_button(self):
        self.ensure_one()
        return {
            'name': 'Attachment.Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('support_ticket_id', '=', self.id)],
        }
    
    def _get_invoice_count(self):
        for ticket in self:
            invoice_ids = self.env['account.move'].search([('invoice_support_ticket_id','=',ticket.id)])
            ticket.invoice_count = len(invoice_ids)
        
    def invoice_button(self):
        self.ensure_one()
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('invoice_support_ticket_id', '=', self.id)],
        }
            
    def _active_ticket(self):
        for s_id in self:
            ticket_ids = self.env['project.task'].search([('ticket_id','=',s_id.id)])
            count = len(ticket_ids)
            s_id.task_count = count
        return
        
    def task(self):
        ticket = {}
        task_obj = self.env['project.task']
        ticket_ids = task_obj.search([('ticket_id','=',self.id)])
        ticket1 = []
        for ticket_id in ticket_ids:
            ticket1.append(ticket_id.id)
        if ticket_ids:
            ticket = self.env['ir.actions.act_window']._for_xml_id('project.action_view_task')
            ticket['domain'] = [('id', 'in', ticket1)]
        return ticket
        
    def _get_avg_ticket_rating(self):
        for review_obj in self:
            avg_ticket_rating = 0.0
            total_messages = len( [x.id for x in review_obj.reviews_ids if x.message_rate > 0] )
            if total_messages > 0:
                total_rate = sum( [x.message_rate for x in review_obj.reviews_ids] )
                avg_ticket_rating = Decimal( total_rate ) / Decimal( total_messages )
            review_obj.avg_ticket_rating = avg_ticket_rating
            
    @api.onchange('support_team_id')
    def onchange_team_id(self):
        res = {}
        if self.support_team_id:
            res = {'user_id': self.support_team_id.user_id,'team_leader_id':self.support_team_id.team_leader}
        return {'value': res}

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = {}
        if self.partner_id:
            res = {'phone': self.partner_id.phone,'email_from':self.partner_id.email}
        return {'value': res}
        
    def change_level(self):
        val = {}
        healdesk_team_id = self.support_team_id
        if healdesk_team_id.parent_team_id:
            parent_team = healdesk_team_id.parent_team_id
            val = {
                    'user_id' : parent_team.user_id,
                    'level' : parent_team.level,
                    'parent_team_id' : parent_team.parent_team_id,
                    'team_leader' : parent_team.team_leader
            }
            healdesk_team_id.update(val)
            self.user_id = val['user_id']
            self.team_leader_id = val['team_leader']
        else:
            raise UserError(_('You are already in Parent Team...!!'))
        return 
        
    def create_invoice(self):
        account_invoice_obj  = self.env['account.move']
        support_invoice_obj = self.env['support.invoice']
        lines = []

        if not self.invoice_option:
            raise UserError(_('Please select Invoice Policy...'))
        else:

            if self.invoice_option == "manual":
                    for inv_line in self.support_invoice_id:
                        lines.append((0,0,{
                                        'product_uom_id': inv_line.uom_id.id,
                                        'name': inv_line.name,
                                        'partner_id':self.partner_id.id,
                                        'quantity':inv_line.quantity,
                                        'price_unit':inv_line.price_unit,
                                        }))
            elif self.invoice_option == "timesheet": 
                if not self.emp_timesheet_cost:
                    raise UserError(_('Please select Timesheet Cost...'))
                else:
                    if not self.timesheet_ids:
                        raise UserError(_('Please Add Employee Timesheet...'))
                    else:
                        if self.emp_timesheet_cost == "employee_cost":
                            for emp_timesheet_id in self.timesheet_ids:
                                lines.append((0,0,{
                                                'product_uom_id': emp_timesheet_id.product_uom_id.id,
                                                'name': emp_timesheet_id.name,
                                                'partner_id':self.partner_id.id,
                                                'quantity':emp_timesheet_id.unit_amount,
                                                'price_unit':emp_timesheet_id.employee_id.hourly_cost,
                                                }))
                        else:
                            for emp_timesheet_id in self.timesheet_ids:
                                lines.append((0,0,{
                                                'product_uom_id': emp_timesheet_id.product_uom_id.id,
                                                'name': emp_timesheet_id.name,
                                                'partner_id':self.partner_id.id,
                                                'quantity':emp_timesheet_id.unit_amount,
                                                'price_unit':self.manual_cost,
                                                }))                        
            invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'currency_id': self.partner_id.currency_id.id,
            'invoice_support_ticket_id':self.id,
            'invoice_line_ids': lines,
            }

            res = self.env['account.move'].create(invoice_vals)
            if res.invoice_support_ticket_id:
                res.invoice_support_ticket_id.write({'invoice_id': res.id})

        return
    
    def _is_assigned_support_ticket(self):
        for rec in self:
            if rec.stage_id.name == "Assigned":
                rec.is_assigned = True
            else:
                rec.is_assigned = False
            return 
    
    @api.model
    def create(self, vals):
        if vals.get('sequence', _('Ticket')) == _('Ticket'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('support.ticket') or _('Ticket')
        if str(vals.get('date_close')) < str(vals.get('date_create')):
            raise UserError(_('Close Date must be greater than Create Date'))

        return super(support_ticket, self).create(vals)

    def write(self, vals):
        if 'date_close' in  vals:
            if str(vals.get('date_close')) < str(self.date_create):
                raise UserError(_('Close Date must be greater than Create Date'))
        if 'stage_id' in vals:
            if vals.get('stage_id'):
                stage_id = self.env['support.stage'].browse(vals.get('stage_id'))
                if stage_id.name == "Closed":
                    vals.update({
                        'stage_id' : stage_id.id,
                        'is_ticket_closed':True,
                        'date_close':datetime.now()
                        })
        return super(support_ticket, self).write(vals)        

    @api.depends('timesheet_ids')
    def _calculate_total_hours(self):
        for ticket in self:
            Hours = 0.0
            if ticket.timesheet_ids:
                for line in ticket.timesheet_ids:
                    Hours += line.unit_amount
            ticket.spend_hours = Hours        


    ''' Website support ticket Field '''
    partner_id = fields.Many2one('res.partner', string="Customer")
    sequence = fields.Char(string='Sequence', readonly=True,copy=False,index=True,default=lambda self: _('Ticket'))
    id = fields.Integer('ID', readonly=True)
    email_from = fields.Char('Email', size=128, help="Destination email for email gateway.")
    phone = fields.Char('Phone')
    category = fields.Many2one('support.ticket.type',string="Category")
    name = fields.Char('Subject', required=True)
    description = fields.Text('Description')
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority')
    stage_id = fields.Many2one ('support.stage', 'Stage', track_visibility='onchange', index=True)
    user_id= fields.Many2one('res.users','Responsible' , store=True, related = "support_team_id.user_id")
    tag_ids = fields.Many2many('project.tags', string='Tags')
    support_team_id = fields.Many2one('support.team',string="Helpdesk Team")
    date_create = fields.Date(string="Create Date" , default=lambda self: fields.Datetime.now())
    date_close = fields.Date(string="Close Date")
    task_count =  fields.Integer(compute='_active_ticket',string="Tasks") 
    timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id', 'Timesheets')
    project_id = fields.Many2one('project.project',string="Project")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    is_ticket_closed = fields.Boolean(string="Is Ticket Closed",readonly=True)
    spend_hours = fields.Monetary("Total Spend Hours", store=True, readonly=True, compute = "_calculate_total_hours")    
    company_id = fields.Many2one('res.company',string="Company" , required = True , default=lambda self: self.env.company)    
    attachment_count  =  fields.Integer('Attachments', compute='_get_attachment_count')
    team_leader_id = fields.Many2one('res.users',string="Team Leader" , related = "support_team_id.team_leader")
    customer_rating = fields.Selection([('1','Poor'), ('2','Average'), ('3','Good'),('4','Excellent')], 'Customer Rating')
    comment = fields.Text(string="Comment")
    invoice_option = fields.Selection([('timesheet','Timesheet'),('manual','Manual')],string="Invoice Policy",default="timesheet")
    emp_timesheet_cost = fields.Selection([('employee_cost','Employee Cost'),('manual_cost','Manual Employee Cost')],string="Timesheet Cost",default="employee_cost")
    support_invoice_id = fields.One2many('support.invoice','support_invoice_id',string="Invoice")
    manual_cost = fields.Monetary(string="Manual Employee Cost",currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    invoice_count  =  fields.Integer('Invoices Count', compute='_get_invoice_count')
    is_assigned = fields.Boolean(compute='_is_assigned_support_ticket',string='Is Assigned',default=False)
    invoice_id = fields.Many2one('account.move', string='Support Invoices', copy=False)

    #DVE FIXME: if partner gets created when sending the message it should be set as partner_id of the ticket.
    def _message_get_suggested_recipients(self):
        recipients = super(support_ticket, self)._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id and ticket.partner_id.email:
                    ticket._message_add_suggested_recipient(recipients, partner=ticket.partner_id, reason=_('Customer Ticket'))
                elif ticket.email_from:
                    ticket._message_add_suggested_recipient(recipients, email=ticket.email_from, reason=_('Customer Ticket Email'))
        except AccessError:  # no read access rights -> just ignore suggested recipients because this implies modifying followers
            pass
        return recipients

    def _ticket_email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        return  [
            x for x in email_list
            if x.split('@')[0] not in self.mapped('support_team_id.alias_name')
        ]


    @api.model
    def message_new(self, msg, custom_values=None):
        model = self._context.get('thread_model') or self._name
        if not ' ' in msg.get('from'):
            user_name= msg.get('from')
        else:
            first_name = msg.get('from').split(" ")[0]
            if msg.get('from').split(" ")[1]:
                last_name = msg.get('from').split(" ")[1]
            fname = first_name.lstrip('"')
            lstname = False
            if last_name:
                lname = last_name.rstrip('"')
            else:
                lstname = fname.rstrip('"')
            if lstname:
                user_name = lstname
            else:
                user_name = fname + " " + lname
        if not ' ' in msg.get('from'):
            user_email= msg.get('from')
        else:
            email = msg.get('from').split(" ")[2]
            email1 = email.lstrip('<')
            user_email = email1.rstrip('>')
        if model == 'support.ticket':
            res_partner = self.env['res.partner'].search([('email', '=', user_email)])
            config_id = self.env['res.config.settings'].search([],order="id desc",limit = 1)
            support_team = self.env['support.team'].search([('id','=',config_id.support_team_id.id)])
            
            search_follower = self.env['mail.followers'].search([('res_model','=',model),('partner_id','=',res_partner.id)])
            res_user_obj = self.env['res.users'].search([('partner_id','=',res_partner.id)])
            
            if res_partner:
                values = dict(custom_values or {}, email_from=res_partner.email, phone=res_partner.phone, partner_id=msg.get('author_id') , support_team_id = support_team.id)
            else:
                cc_name = user_email.split('@')
                partner_id = self.env['res.partner'].create({
                            'name' : str(user_name),
                            'email': str(user_email)
                            })    
                values = dict(custom_values or {}, email_from=user_email, partner_id=msg.get('author_id'), support_team_id = support_team.id)
        return super(support_ticket, self).message_new(msg, custom_values=values)

    def message_update(self, msg, update_vals=None):
        partner_ids = [x for x in self._mail_find_partner_from_emails(self._ticket_email_split(msg)) if x]
        if partner_ids:
            self.message_subscribe(partner_ids)
        return super(support_ticket, self).message_update(msg, update_vals=update_vals)

    def _message_post_after_hook(self, message, *args, **kwargs):
        if self.email_from and self.partner_id and not self.partner_id.email:
            self.partner_id.email = self.email_from

        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email_from)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email_from', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        return super(support_ticket, self)._message_post_after_hook(message, *args, **kwargs)


    @api.model
    def get_empty_list_help(self, help):
        help_title, sub_title = "", ""
        if self._context.get('default_type') == 'lead':
            help_title = _('Create a new lead')
        else:
            help_title = _('Create an opportunity in your pipeline')
        alias_record = self.env['mail.alias'].search([
            ('alias_name', '!=', False),
            ('alias_name', '!=', ''),
            ('alias_model_id.model', '=', 'support.ticket'),
            ('alias_parent_model_id.model', '=', 'support.team'),
            ('alias_force_thread_id', '=', False)
        ], limit=1)
        if alias_record and alias_record.alias_domain and alias_record.alias_name:
            email = '%s@%s' % (alias_record.alias_name, alias_record.alias_domain)
            email_link = "<a href='mailto:%s'>%s</a>" % (email, email)
            sub_title = _('or send an email to %s') % (email_link)
        return '<p class="o_view_nocontent_smiling_face">%s</p><p class="oe_view_nocontent_alias">%s</p>' % (help_title, sub_title)


    def _notify_get_reply_to(self, default=None):
        """ Override to set alias of tickets to their team if any. """
        aliases = self.mapped('support_team_id')._notify_get_reply_to(default=default)
        res = {ticket.id: aliases.get(ticket.support_team_id.id) for ticket in self}
        leftover = self.filtered(lambda rec: not rec.support_team_id)
        if leftover:
            res.update(super(support_ticket, leftover)._notify_get_reply_to(default=default))
        return res

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def signup_get_auth_param(self):
        """ Get a signup token related to the partner if signup is enabled.
            If the partner already has a user, get the login parameter.
        """
        ticket = self.env['support.ticket'].search([('partner_id','=',self.id)],limit=1)
        if ticket:
            pass
        else:
            if not self.env.user.has_group('base.group_user') and not self.env.is_admin():
                raise exceptions.AccessDenied()

        res = defaultdict(dict)

        allow_signup = self.env['res.users']._get_signup_invitation_scope() == 'b2c'
        for partner in self:
            partner = partner.sudo()
            if allow_signup and not partner.user_ids:
                partner.signup_prepare()
                res[partner.id]['auth_signup_token'] = partner.signup_token
            elif partner.user_ids:
                res[partner.id]['auth_login'] = partner.user_ids[0].login
        return res
