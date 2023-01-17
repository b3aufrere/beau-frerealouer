# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


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
    
    @api.onchange('territory_id')
    def onchange_territory_id(self):
        for lead in self:
            if not lead.territory_id:
                lead.user_id = False