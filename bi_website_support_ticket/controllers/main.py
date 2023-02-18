# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import werkzeug
import json
import base64

import odoo.http as http
from odoo.http import request
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta, time
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import odoo.http as http

class EditTicket(http.Controller):

    @http.route(['/edit_ticket/<model("support.ticket"):ticket>'], type='http', auth="public", website=True)
    def edit_timesheet(self, ticket, category='', search='', **kwargs):
        return request.render("bi_website_support_ticket.bi_portal_edit_ticket",{'ticket':ticket})

    @http.route(['/my/save_edit_ticket'], type='http', auth="public", website=True)
    def edit_ticket_save(self,context=None,**post):
        if post:
            name = post['name']
            email_from = post['email_from']
            customer = post['customer']
            team = post['team']
            phone = post['phone']
            priority = post['priority']
            project = post['project']
            category = post['category']
            desc = post['desc']
            
        ticket_id = str(post['ticket_id'])
        if project:
            project_obj = request.env['project.project'].sudo().search([('id','=',project)])
            project_project = project_obj.id
        else:
            project_project = False
        if customer:
            partner_obj = request.env['res.partner'].sudo().search([('id','=',customer)])
            res_partner = partner_obj.id
        else:
            res_partner = False
        if team:
            team_obj = request.env['support.team'].sudo().search([('id','=',team)])
            support_team = team_obj.id
        else:
            support_team = False
        if category:
            category_obj = request.env['support.ticket.type'].sudo().search([('id','=',category)])
            type_id = category_obj.id
        else:
            type_id = False

        ticket_obj = request.env['support.ticket'].sudo().search([('id','=',ticket_id)])
        
        ticket_obj.update({
            'name':name,
            'email_from': email_from,
            'phone': phone,
            'project_id': project_project,
            'support_team_id': support_team,
            'partner_id': res_partner,
            'priority': priority,
            'description': desc,
            'category': type_id, 
        })
        return request.redirect("/my/ticket")

class SupportTicket(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(SupportTicket, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        
        support_ticket = request.env['support.ticket']
        partner_ticket_count = support_ticket.sudo().search([('partner_id','=',partner.id)])
        ticket_count = support_ticket.sudo().search_count(['|',('partner_id','=',partner.id),('user_id','=',request.env.user.id)])
        values.update({
            'ticket_count': ticket_count,
        })
        return values
        
    @http.route(['/my/ticket', '/my/ticket/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_ticket(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        support_ticket = request.env['support.ticket']

        domain = []
        # count for pager
        ticket_count = support_ticket.sudo().search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/ticket",
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        partner = request.env.user.partner_id
        supports = support_ticket.sudo().search(['|',('partner_id','=',partner.id),('user_id','=',request.env.user.id)], offset=pager['offset'])
        request.session['my_ticket_history'] = supports.ids[:100]

        values.update({
            'supports': supports.sudo(),
            'page_name': 'ticket',
            'pager': pager,
            'default_url': '/my/ticket',
        })
        return request.render("bi_website_support_ticket.portal_my_ticket", values)
        
        
    @http.route('/support_ticket', type="http", auth="public", website=True)
    def submit_support_ticket(self, **kw):
        """Let's public and registered user submit a support ticket"""
        name = ""
        if http.request.env.user.name != "Public user":
            name = http.request.env.user.name
        
        customer = http.request.env.user.partner_id.name
        email = http.request.env.user.partner_id.email
        phone = http.request.env.user.partner_id.phone
        values = {'partner_id' : customer,'user_ids': name,'email':email,'phone':phone}
        
        return http.request.render('bi_website_support_ticket.submit_support_ticket', values)
    
    @http.route('/support_ticket/thanks', type="http", auth="public", website=True)
    def support_ticket_thanks(self, **post):
        """Displays a thank you page after the user submits a support ticket"""
        if post.get('debug'):
            return request.render("bi_website_support_ticket.support_thank_you")

        if post.get('fw'):
            return request.render("bi_website_support_ticket.support_thank_you")

        partner_brw = request.env['res.users'].sudo().browse(request.uid)
        Attachments = request.env['ir.attachment']
        if post:
            upload_file = post['upload']

            if post['support_team_id'] == '':
                support_team_obj = False
                user_id = False
                team_leader_id = False
            else:
                support_team_obj = request.env['support.team'].sudo().browse(int(post['support_team_id']))
                user_id = support_team_obj.user_id.id
                team_leader_id = support_team_obj.user_id.id
            
            name = post['name']
            description = post['description']
            email_from = post['email_from']
            phone = post['phone']
            category = post['ticket_id']
            priority = post['priority']
            date_create = datetime.now()
            if post['support_team_id']:
                support_team_id = int(post['support_team_id'])
            else:
                support_team_id = post['support_team_id']

            vals = {
                    'name':name,
                    'description':description,
                    'email_from': email_from,
                    'phone': phone,
                    'category': category,
                    'priority' : priority,
                    'partner_id': partner_brw.partner_id.id,
                    'date_create' : date_create,
                    'support_team_id' : support_team_id or False,
                    'user_id' : user_id or False,
                    'team_leader_id' : team_leader_id or False,
                    }

            support_ticket_obj = request.env['support.ticket'].sudo().create(vals)
            if upload_file:
                attachment_id = Attachments.sudo().create({
                    'name': upload_file.filename,
                    'type': 'binary',
                    'datas': base64.encodebytes(upload_file.read()),
                    'name': upload_file.filename,
                    'public': True,
                    'res_model': 'ir.ui.view',
                    'res_id': False,
                    'support_ticket_id' : support_ticket_obj.id,
                })

            helpdesk_manager_id = request.env['ir.model.data'].sudo().\
            _xmlid_lookup('bi_website_support_ticket.group_support_manager')[2]
            group_manager = request.env['res.groups'].sudo().browse(helpdesk_manager_id)
            if group_manager.users:
                for group_manager in group_manager.users:
                    template_id = request.env['ir.model.data'].sudo()._xmlid_lookup('bi_website_support_ticket.email_template_support_ticket')[2]
                    email_template_obj = request.env['mail.template'].sudo().browse(template_id)
                    # email_template_obj.sudo().send_mail(support_ticket_obj.id, force_send=True)
                    if template_id:
                        values = email_template_obj.generate_email(support_ticket_obj.id, fields=['body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                        values['email_from'] = group_manager.partner_id.email
                        if email_from:
                            values['email_to'] = email_from
                        else:
                            values['email_to'] = request.env.user.email
                        values['author_id'] = group_manager.partner_id.id
                        values['subject'] = name
                        mail_mail_obj = request.env['mail.mail']
                        msg_id = mail_mail_obj.sudo().create(values)
                        if upload_file:
                            msg_id.attachment_ids=[(6,0,[attachment_id.id])]
                        if msg_id:
                            mail_mail_obj.send([msg_id])
                        
        return request.render("bi_website_support_ticket.support_thank_you")
    
    @http.route('/ticket/view', type="http", auth="user", website=True)
    def ticket_view_list(self, **kw):
        """Displays a list of ticket owned by the logged in user"""
        return http.request.render('bi_website_support_ticket.ticket_view_list')
    
    @http.route(['/ticket/view/detail/<model("support.ticket"):ticket>'],type='http',auth="public",website=True)
    def support_ticket_view(self, ticket, category='', search='', **kwargs):
        context = dict(request.env.context or {})
        ticket_obj = request.env['support.ticket']
        context.update(active_id=ticket.id)
        portal = request.env.user.has_group('base.group_portal')

        ticket_data_list = []
        ticket_data = ticket_obj.sudo().browse(int(ticket))
        
        for items in ticket_data:
            ticket_data_list.append(items)
        
        if portal:
            return http.request.render('bi_website_support_ticket.support_ticket_view',{
            'ticket_data_list': ticket,
            }) 
        else:
            return http.request.render('bi_website_support_ticket.support_ticket_view',{
            'ticket_data_list': ticket,
            'portal':'portal'
            })

    @http.route(['/ticket/message'],type='http',auth="public",website=True)
    def ticket_message(self, **post):
        
        Attachments = request.env['ir.attachment']
        upload_file = post['upload']
        
        if ',' in post.get('ticket_id'):
            bcd = post.get('ticket_id').split(',')
        else : 
            bcd = [post.get('ticket_id')]
            
        support_obj = request.env['support.ticket'].sudo().search([('id','=',bcd)])            
            
        if upload_file:
            attachment_id = Attachments.sudo().create({
                'name': upload_file.filename,
                'type': 'binary',
                'datas': base64.encodebytes(upload_file.read()),
                'datas_fname': upload_file.filename,
                'public': True,
                'res_model': 'ir.ui.view',
                'support_ticket_id' : support_obj.id,
            }) 
        
        context = dict(request.env.context or {})
        ticket_obj = request.env['support.ticket']
        if post.get( 'message' ):
            message_id1 = support_obj.message_post() 
                
            message_id1.body = post.get( 'message' )
            message_id1.type = 'comment'
            message_id1.subtype = 'mt_comment'
            message_id1.model = 'support.ticket'
            message_id1.res_id = post.get( 'ticket_id' )
                    
        return http.request.render('bi_website_support_ticket.support_message_thank_you') 
        
    @http.route(['/ticket/comment/<model("support.ticket"):ticket>'],type='http',auth="public",website=True)
    def ticket_comment_page(self, ticket,**post): 
        
        return http.request.render('bi_website_support_ticket.support_ticket_comment',{'ticket': ticket}) 
     
    @http.route(['/support_ticket/comment/send'],type='http',auth="public",website=True)
    def ticket_comment(self, **post):
        context = dict(request.env.context or {})
        if post.get('ticket_id'):
            ticket_obj = request.env['support.ticket'].sudo().browse(int(post['ticket_id']))
            ticket_obj.update({
                    'customer_rating' : post['customer_rating'],            
                    'comment' : post['comment'],
            })
        return http.request.render('bi_website_support_ticket.support_rating_thank_you')         
              
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
