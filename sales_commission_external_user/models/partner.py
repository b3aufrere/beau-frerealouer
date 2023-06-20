# -*- coding: utf-8 -*-
#from openerp import models, fields, api
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_commission_user_ids = fields.One2many(
        'sale.commission.level.users',
        'partner_id',
        string="Sale Commission User"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
