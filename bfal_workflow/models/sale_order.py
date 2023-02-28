# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    meeting_ids = fields.One2many('calendar.event', 'order_id', string="Rendez-vous")
    meeting_count = fields.Integer(compute='_compute_meeting_count', string="Nombre des rendez-vous")
    division_id = fields.Many2one('division', related='user_id.employee_id.branch_id.division_id', string='Division')
    # entreprise_id = fields.Many2one('entreprise', related='user_id.employee_id.entreprise_id', string='Entreprise')
    branch_id = fields.Many2one('res.branch', related='user_id.employee_id.branch_id', string='Entreprise')

    @api.depends('meeting_ids')
    def _compute_meeting_count(self):
        for order in self:
            order.meeting_count = len(order.meeting_ids)
    
    def action_view_meetings(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_order_id': self.id,
        }
        
        action['domain'] = expression.AND([[('order_id', '=', self.id)]])
        meeting_ids = self.meeting_ids.filtered_domain([('order_id', '=', self.id)])
        
        if len(meeting_ids) == 1:
            action['views'] = [(self.env.ref('calendar.view_calendar_event_form').id, 'form')]
            action['res_id'] = meeting_ids.id
        
        return action

    def action_create_rendez_vous(self):
        if not self.partner_id:
            pass
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("bfal_workflow.meeting_action_new_from_sale")
            if action:
                action['context'] = {
                    'default_partner_ids': [(4, [self.user_id.partner_id.id]), (4, [self.partner_id.id])],
                    'default_name': self.opportunity_id.name if self.opportunity_id else '',
                    'default_description': self.opportunity_id.description if self.opportunity_id else '',
                    'default_order_id': self.id                     
                }
                
                return action