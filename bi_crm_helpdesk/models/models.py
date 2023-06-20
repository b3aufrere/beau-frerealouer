# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class crmlead(models.Model):
    _inherit = 'crm.lead'

    crm_lead_ticket_id = fields.Many2one('support.ticket', 'Support Ticket')
    crm_lead_ticket_count = fields.Integer('CRM Lead Ticket Count', compute='_get_crm_lead_ticket_count')

    def create_ticket(self):
        support_ticket_obj = self.env['support.ticket']
        name = "Issue of " + self.name
        vals = {
            'name': name,
            'partner_id': self.partner_id.id,
            'crm_lead_id': self.id
        }
        support_ticket_obj = self.env['support.ticket'].sudo().create(vals)

        if support_ticket_obj.crm_lead_id:
            support_ticket_obj.crm_lead_id.write({'crm_lead_ticket_id': support_ticket_obj.id})
        return {
            'name': _('Support Ticket'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'support.ticket',
            'res_id': support_ticket_obj.id
        }

    def crm_lead_button(self):
        self.ensure_one()
        return {
            'name': 'Suppor Ticket',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'support.ticket',
            'domain': [('crm_lead_id', '=', self.id)],
        }

    def _get_crm_lead_ticket_count(self):
        for ticket in self:
            ticket_ids = self.env['support.ticket'].search([('crm_lead_id', '=', ticket.id)])
            ticket.crm_lead_ticket_count = len(ticket_ids)


class support_ticket(models.Model):
    _inherit = 'support.ticket'

    crm_lead_count = fields.Integer('CRM Lead Count', compute='_get_crm_lead_count')
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead', copy=False)

    def create_crm_lead(self):
        crm_lead_obj = self.env['crm.lead']
        crm_lead_obj_id = crm_lead_obj.create({
            'partner_id': self.partner_id.id,
            'name': self.partner_id.name,
            'email_from': self.partner_id.email,
            'phone': self.partner_id.phone,
            'crm_lead_ticket_id': self.id
        })
        if crm_lead_obj_id.crm_lead_ticket_id:
            crm_lead_obj_id.crm_lead_ticket_id.write({'crm_lead_id': crm_lead_obj_id.id})

        return

    def crm_lead_button(self):
        self.ensure_one()
        return {
            'name': 'CRM Lead',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'domain': [('crm_lead_ticket_id', '=', self.id)],
        }

    def _get_crm_lead_count(self):
        for ticket in self:
            crm_lead_ids = self.env['crm.lead'].search([('crm_lead_ticket_id', '=', ticket.id)])
            ticket.crm_lead_count = len(crm_lead_ids)
