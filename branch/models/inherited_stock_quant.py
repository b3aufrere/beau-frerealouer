# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def default_get(self, default_fields):
        res = super(StockQuant, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id' : self.env.user.branch_id.id or False
            })
        return res

    branch_id = fields.Many2one('res.branch', string="Branch")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({'branch_id':self.env.user.branch_id.id})
        return super(StockQuant, self).create(vals_list)

    def write(self, vals):
        vals.update({'branch_id':self.env.user.branch_id.id})
        return super(StockQuant, self).write(vals)
    
    @api.model
    def _get_inventory_fields_create(self):
        res = super(StockQuant, self)._get_inventory_fields_create()
        res.append('branch_id')
        return res


    @api.model
    def _get_inventory_fields_write(self):
        res = super(StockQuant, self)._get_inventory_fields_write()
        res.append('branch_id')
        return res

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")



    def action_apply_inventory(self):
        res = super(StockQuant, self).action_apply_inventory()
        for quant in self:
            quant.branch_id = self.env.user.branch_id.id or False
        return res

