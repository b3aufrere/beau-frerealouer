# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.mail import is_html_empty


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    territory_id = fields.Many2one(
        'territory',
        string='Territoire de travail'
    )

    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), '&', ('company_ids', 'in', user_company_ids), '&', ('employee_id', '!=', False), '&', ('employee_id.territory_id', '!=', False), ('employee_id.territory_id', '=', territory_id)]",
        check_company=True, index=True, tracking=True)
    
    state_name = fields.Char(related='stage_id.name', store=True, readonly=False, string="Nom d'état")

    is_worker = fields.Boolean(default=False, compute="compute_is_worker")

    is_accepted = fields.Boolean(default=False, compute="compute_is_accepted", string="Est accepté ?")

    @api.onchange('sale_order_count')
    def compute_is_accepted(self):
        self.is_accepted = True if self.order_ids else False

    @api.onchange('user_id')
    def compute_is_worker(self):
        self.is_worker = True if self.user_id and self.user_id.id == self.env.user.id else False
    
    @api.onchange('territory_id')
    def onchange_territory_id(self):
        for lead in self:
            if not lead.territory_id:
                lead.user_id = False
    
    def action_accept_lead(self):
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
            'default_internal_note': self.description,
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
        stage_id = self.env['crm.stage'].search([('name', '=', 'Rejeté')])
        if 'not_accept' in self._context:
            stage_id = self.env['crm.stage'].search([('name', '=', 'Non accepté')])
        
        res = False

        if stage_id:
            res = True
            self.stage_id = stage_id.id
            if additional_values:
                self.write(dict(additional_values))
        
        return res
    
    def action_not_accept_lead(self):
        return self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_lost_action")