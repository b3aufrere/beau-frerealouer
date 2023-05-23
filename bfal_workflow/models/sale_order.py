# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    meeting_ids = fields.One2many('calendar.event', 'order_id', string="Rendez-vous")
    meeting_count = fields.Integer(compute='_compute_meeting_count', string="Nombre des rendez-vous")
    division_id = fields.Many2one('division', related='branch_id.division_id', string='Division')
    # entreprise_id = fields.Many2one('entreprise', related='user_id.employee_id.entreprise_id', string='Entreprise')
    branch_id = fields.Many2one('res.branch', string='Entreprise')
    task_assignment_history_ids = fields.One2many('task.assignment.history', 'order_id', string="Historique des assignations")
    state = fields.Selection(selection_add=[('not_accepted', 'Non accepté')])
    order_not_accept_reason_id = fields.Many2one('order.not.accept.reason', string="Motif de non acceptation",)
    description = fields.Html(string='Description')
    payment_term_id = fields.Many2one(default=lambda self: self.env.ref("account.account_payment_term_immediate").id)
    user_id = fields.Many2one(
        domain=lambda self: "['&', ('groups_id', '=', {}), '&', ('share', '=', False), '&', ('company_ids', '=', company_id), \
                              '|', '&', ('employee_id.branch_id', '!=', False), ('employee_id.branch_id', '=', branch_id), \
                              ('employee_id.branch_id', '=', False)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ))

    # @api.onchange('branch_id')
    # def onchange_branch_id(self):
    #     self.user_id = False

    @api.depends('partner_id')
    def _compute_payment_term_id(self):
        for order in self:
            order.payment_term_id = self.env.ref("account.account_payment_term_immediate").id

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
    
    def action_not_accepted(self):
        return {
            'name':_("Non acceptation"),
            'view_mode': 'form',
            'view_id': self.env.ref("bfal_workflow.view_order_not_accept_wiz_form").id,
            'res_model': 'order.not.accept.wiz',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
            }
        }

    def action_reassign(self):
        return {
            'name':_("Réassignation"),
            'view_mode': 'form',
            'view_id': self.env.ref("bfal_workflow.view_order_reassignment_form").id,
            'res_model': 'reassignment',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
            }
        }