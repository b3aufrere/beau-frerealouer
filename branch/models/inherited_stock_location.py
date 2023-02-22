# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    branch_id = fields.Many2one('res.branch')

    @api.constrains('branch_id')
    def _check_branch(self):
        warehouse_obj = self.env['stock.warehouse']
        warehouse_id = warehouse_obj.search(
            ['|', '|', ('wh_input_stock_loc_id', '=', self.id),
             ('lot_stock_id', '=', self.id),
             ('wh_output_stock_loc_id', '=', self.id)])
        for warehouse in warehouse_id:
            if self.branch_id != warehouse.branch_id:
                raise UserError(_('Configuration error\nYou  must select same branch on a location as assigned on a warehouse configuration.'))

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")

