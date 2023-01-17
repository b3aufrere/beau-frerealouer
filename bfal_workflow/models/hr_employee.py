# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    entreprise_id = fields.Many2one(
        'entreprise',
        string='Entreprise',
        groups="hr.group_hr_user"
    )

    territory_id = fields.Many2one(
        'territory',
        string='Territoire de travail',
        groups="hr.group_hr_user",
        domain="[('entreprise_ids', 'in', entreprise_id)]"
    )