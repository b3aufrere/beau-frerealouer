from odoo import models, fields, api, _
from odoo.exceptions import UserError

from logging import warning as w

class TipAssignAmount(models.TransientModel):
    _name = 'tip.assign.amount'
    _description = 'Tip Amount'
    
    tip_amount = fields.Float(string="Pourcentage de pourboire (%)")
   
    def action_assign_tip(self):
        move_obj = self.env['account.move']
        tip_product_id = self.env.company.tip_product_id
        if not tip_product_id:
            raise UserError(_('Please Configuer a Tip Product'))
        if self.env.context.get('active_id'):
            move_id = move_obj.browse(self.env.context.get('active_id'))
            lines = move_id.invoice_line_ids.filtered(lambda line : line.product_id.id ==  tip_product_id.id)
            tip_value = move_id.amount_untaxed * (float(self.tip_amount) / 100)
            if lines:
                lines.write({
                    'quantity': 1,
                    'price_unit':tip_value,
                    'tax_ids': [(5, 0)]
                })
            else:
                move_id.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': tip_product_id.id,
                        'product_uom_id': tip_product_id.uom_id.id,
                        'name': tip_product_id.display_name,
                        'quantity': 1,
                        'price_unit':tip_value,
                        'tax_ids': []
                    })]
                })

