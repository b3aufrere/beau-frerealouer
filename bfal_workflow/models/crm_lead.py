# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, Command
from datetime import date
from odoo.tools import html2plaintext, plaintext2html
from odoo.exceptions import UserError
import json


from logging import warning as w


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # territory_id = fields.Many2one(
    #     'territory',
    #     string='Territoire de travail'
    # )

    extra_notes = fields.Html(string='Définition')

    task_type = fields.Selection(
        [
            ('hourly_service', "Service à l'heure"),
            ('quote_request', 'Demande de soumission')
        ],
        string="Type de travail",
        default=""
    )

    request_src = fields.Selection(
        [
            ('email', 'Email'),
            ('call', 'Appel'),
            ('website', 'Site web'),
            ('chatbox', 'Chatbox'),
        ],
        string="Source de demande",
        default=""
    )

    division_id = fields.Many2one(
        'division',
        string='Division'
    )

    branch_id = fields.Many2one(
        'res.branch',
        string='Entreprise',
        domain="[('division_id', '=', division_id)]"
    )

    user_id = fields.Many2one(
        'res.users', string='Partenaire assignée',default=False,
        domain="['&', ('share', '=', False), '&', ('company_ids', 'in', user_company_ids), '&', ('employee_id', '!=', False), '|', '&', ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', branch_id), ('employee_id.branch_id', '=', False)]",
        # domain="[('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True)
    
    salesperson_id = fields.Many2one('res.users', string='Vendeur', default=False,
        domain="['&', ('share', '=', False), '&', ('company_ids', 'in', user_company_ids), '&', ('employee_id', '!=', False), '|', '&', ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', branch_id), ('employee_id.branch_id', '=', False)]",
        # domain="[('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True)
    
    state_name = fields.Char(related='stage_id.name', store=True, readonly=False, string="Nom d'état")

    is_decision_stage = fields.Boolean(related='stage_id.is_decision_stage', store=True, readonly=False, string="Est l'étape de la décision")

    is_worker = fields.Boolean(default=False, compute="compute_is_worker")

    is_accepted = fields.Boolean(default=False, compute="compute_is_accepted", string="Est accepté ?")

    state_role = fields.Selection(
        [
            ('new', 'Nouveau'),
            ('to_assign', 'À assigner'),
            ('assigned', 'Assigné'),
            ('in_progress', 'En cours'),
            ('done', 'Fait'),
            ('claim', 'Réclamation'),
            ('rejected', 'Rejeté'),
            ('service_not_available', 'Service non disponible'),
        ],
        string="Rôle",
        related='stage_id.role'
    )
    
    def _prepare_opportunity_quotation_context(self):
        quotation_context = super(CrmLead, self)._prepare_opportunity_quotation_context()

        if self.branch_id:
            quotation_context['default_branch_id'] = self.branch_id.id
        
        if self.user_id:
            quotation_context['default_user_id'] = self.user_id.id
        
        w(f"quotation_context >>> {json.dumps(quotation_context, indent=4)}")

        return quotation_context

    @api.onchange('sale_order_count')
    def compute_is_accepted(self):
        self.is_accepted = True if self.order_ids else False

    @api.onchange('user_id')
    def compute_is_worker(self):
        self.is_worker = True if self.user_id and self.user_id.id == self.env.user.id else False
    
    @api.onchange('branch_id')
    def onchange_branch_id(self):
        for lead in self:
            if not lead.branch_id:
                lead.user_id = False
    
    def action_accept_lead(self):
        for lead in self:
            stage_assigned_id = self.env['crm.stage'].search([('is_assign_stage', '=', True)], limit=1)
            
            if stage_assigned_id:
                if lead.stage_id and lead.stage_id.id != stage_assigned_id.id:
                    lead.stage_id =  stage_assigned_id.id
            else:
                raise UserError("Il faut ajouté une étape d'attribution")
        return self.action_sale_quotations_new()

    def _prepare_opportunity_quotation_context(self):
        """ Prepares the context for a new quotation (sale.order) by sharing the values of common fields """
        self.ensure_one()
        quotation_context = {
            'default_opportunity_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_description': self.description,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': [(6, 0, self.tag_ids.ids)]
        }
        if self.team_id:
            quotation_context['default_team_id'] = self.team_id.id
        if self.user_id:
            quotation_context['default_user_id'] = self.user_id.id
        return quotation_context
    
    def action_service_send(self):
        self.ensure_one()
        mail_template = self.env.ref('bfal_workflow.mail_template_accept_service', raise_if_not_found=False)
        
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)

    def action_set_lost(self, **additional_values):
        """ Lost semantic: probability = 0 or active = False """
        stage_id = self.env['crm.stage'].search([('role', '=', 'rejected')], limit=1)

        if stage_id:
            self.stage_id = stage_id.id
        else:
            raise UserError("Il faut ajouté une étape avec le rôle 'Rejeté'")
        
        if 'not_accept' in self._context:
            stage_id = self.env['crm.stage'].search([('name', '=', 'Non accepté')])
        
        res = False 

        if stage_id:
            res = True
            self.stage_id = stage_id.id
            self.user_id = False
            if additional_values:
                self.write(dict(additional_values))
        
        return res
    
    def action_not_accept_lead(self):
        return self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_lost_action")
    
    @api.depends('stage_id')
    def _compute_date_last_stage_update(self):
        super(CrmLead, self)._compute_date_last_stage_update()

        for lead in self:
            if lead.stage_id:
                if lead.stage_id.mail_template_id:
                    lead.stage_id.mail_template_id.send_mail(lead.id, force_send=True)
                
                if lead.stage_id.sms_template_id:
                    twilio_sms_accounts = self.env['twilio.sms.gateway.account'].sudo().search([('state', '=', 'confirmed')], order="id asc")
                    tobe_twilio_sms_accounts = twilio_sms_accounts.filtered(lambda x: x.is_default_sms_account)
                    twilio_sms_account = False
                    
                    if tobe_twilio_sms_accounts:
                        twilio_sms_account = tobe_twilio_sms_accounts[0]
                    elif twilio_sms_accounts:
                        twilio_sms_account = twilio_sms_accounts[0]
                    
                    if twilio_sms_account:
                        if lead.id and lead.user_id and lead.user_id.partner_id and lead.user_id.partner_id.phone:
                            message = lead._message_sms_with_template_twilio(
                                    template=lead.stage_id.sms_template_id,
                                )
                            message = html2plaintext(message) #plaintext2html(html2plaintext(message))
                            
                            datas = {
                                "From": twilio_sms_account.account_from_mobile_number,
                                "To": (lead.user_id.partner_id.phone or "").replace(" ", ""),
                                "Body": message
                            }
                            twilio_sms_account.send_sms_to_recipients_from_another_src(datas)
                            lead.message_post(body="SMS ENVOYÉ" + plaintext2html(html2plaintext(message)), message_type='sms')
                
                if lead.stage_id.mail_activity_type_id and lead.user_id:
                    activity_id = self.env['mail.activity'].create({
                        'activity_type_id': lead.stage_id.mail_activity_type_id.id,
                        'user_id': lead.user_id.id,
                        'summary': lead.stage_id.mail_activity_type_id.summary,
                        # 'date_deadline': date.today(),
                        'res_id': lead.id,
                        'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'crm.lead')]).id
                    })

                    if activity_id:
                        activity_id.date_deadline = activity_id._calculate_date_deadline(activity_id.activity_type_id)
                        activity_id.action_close_dialog()
                

    def action_service_not_available(self):
        for lead in self:
            stage_service_not_available_id = self.env['crm.stage'].search([('role', '=', 'service_not_available')], limit=1)

            if stage_service_not_available_id:
                lead.stage_id = stage_service_not_available_id.id
            else:
                raise UserError("Il faut ajouté une étape avec le rôle 'Service non disponible'")
    
    # def write(self, vals):
    #     w(">>>>>>>> write lead")
    #     res = super(CrmLead, self).write(vals)

    #     if 'update_stage' not in self._context:
    #         for lead in self:
    #             w(f"sale_order_count >> {lead.sale_order_count}")
    #             w(f"quotation_count >> {lead.quotation_count}")
    #             w(f"state_role >> {lead.state_role}")

    #             if lead.sale_order_count > 0 and lead.state_role in ('new', 'to_assign'):
    #                 stage_assigned_id = self.env['crm.stage'].search([('role', '=', 'assigned')], limit=1)

    #                 if stage_assigned_id:
    #                     lead.with_context({'update_stage':True}).write({
    #                         'stage_id':stage_assigned_id.id 
    #                     }) 
    #                 else:
    #                     raise UserError("Il faut ajouté une étape avec le rôle 'Assigné'") 
                    
    #             elif lead.quotation_count > 0 and lead.state_role == 'new':
    #                 stage_to_assign_id = self.env['crm.stage'].search([('role', '=', 'to_assign')], limit=1)

    #                 if stage_to_assign_id:
    #                     lead.with_context({'update_stage':True}).write({
    #                         'stage_id':stage_to_assign_id.id 
    #                     })
    #                 else:
    #                     raise UserError("Il faut ajouté une étape avec le rôle 'À assigner'")

    #     return res
    

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order', 'order_ids.company_id')
    def _compute_sale_data(self):
        # w("lead >>>>>>>> _compute_sale_data")
        res = super(CrmLead, self)._compute_sale_data()

        for lead in self:
                # w(f"sale_order_count >> {lead.sale_order_count}")
                # w(f"quotation_count >> {lead.quotation_count}")
                # w(f"state_role >> {lead.state_role}")

                if lead.sale_order_count > 0 and lead.state_role in ('new', 'to_assign'):
                    stage_assigned_id = self.env['crm.stage'].search([('role', '=', 'assigned')], limit=1)

                    if stage_assigned_id:
                        lead.stage_id = stage_assigned_id.id 
                    else:
                        raise UserError("Il faut ajouté une étape avec le rôle 'Assigné'") 
                    
                elif lead.quotation_count > 0 and lead.state_role != 'to_assign':
                    stage_to_assign_id = self.env['crm.stage'].search([('role', '=', 'to_assign')], limit=1)

                    if stage_to_assign_id:
                        lead.stage_id = stage_to_assign_id.id 
                    else:
                        raise UserError("Il faut ajouté une étape avec le rôle 'À assigner'")      

        return res
    
    # @api.depends('activity_date_deadline')
    # def _compute_kanban_state(self):
    #     res = super(CrmLead, self)._compute_kanban_state()

    #     for lead in self:
    #         if lead.sale_order_count > 0 and self.state_role in ('new', 'to_assign'):
    #             stage_assigned_id = self.env['crm.stage'].search([('role', '=', 'assigned')], limit=1)

    #             if stage_assigned_id:
    #                 lead.stage_id = stage_assigned_id.id   
    #             else:
    #                 raise UserError("Il faut ajouté une étape avec le rôle 'Assigné'") 
                
    #         elif lead.quotation_count > 0 and self.state_role == 'new':
    #             stage_to_assign_id = self.env['crm.stage'].search([('role', '=', 'to_assign')], limit=1)

    #             if stage_to_assign_id:
    #                 lead.with_context({'update_stage':True}).write({
    #                     'stage_id':stage_to_assign_id.id 
    #                 })
    #             else:
    #                 raise UserError("Il faut ajouté une étape avec le rôle 'À assigner'")  
        
    #     return res
    
    # @api.model
    # def default_get(self, default_fields):
    #     res = super(CrmLead, self).default_get(default_fields)

    #     if self.state_role != 'assigned':
    #         if self.sale_order_count > 0:
    #             stage_assigned_id = self.env['crm.stage'].search([('role', '=', 'assigned')], limit=1)

    #             if stage_assigned_id:
    #                 self.stage_id = stage_assigned_id.id   
    #             else:
    #                 raise UserError("Il faut ajouté une étape avec le rôle 'Assigné'") 
                
    #         elif self.quotation_count > 0:
    #             stage_to_assign_id = self.env['crm.stage'].search([('role', '=', 'to_assign')], limit=1)

    #             if stage_to_assign_id:
    #                 self.with_context({'update_stage':True}).write({
    #                     'stage_id':stage_to_assign_id.id 
    #                 })
    #             else:
    #                 raise UserError("Il faut ajouté une étape avec le rôle 'À assigner'")

    #     return res
        