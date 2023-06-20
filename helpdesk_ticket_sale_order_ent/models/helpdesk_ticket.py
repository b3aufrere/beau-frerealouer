# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
   
    support_sale_line_ids = fields.One2many(
        'support.sales.line.custom',
        'help_support_id',
        string='Quotation Lines',
        copy=True
    )
    def custom_action_show_sale_order(self):
        self.ensure_one()
        res = self.env.ref('sale.action_quotations_with_onboarding')
        res = res.sudo().read()[0]
        res['domain'] = str([('helpdesk_custom_ticket_id','=',self.id)])
        return res
    

    def action_create_sale_order(self):
        self.ensure_one()
        if not self.support_sale_line_ids:
            raise UserError(_("Please add product lines for quotation purpose."))
        action = self.env.ref('sale.action_quotations_with_onboarding').sudo().read()[0]
        # action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        # line_list = []
        # for line in self.support_sale_line_ids:
        #     if not line.order_line_id:
        #         line_list.append((0, 0, {
        #             'product_id': line.product_id.id,
        #             'product_uom_qty': line.quantity,
        #             'product_uom': line.product_uom.id,
        #             'price_unit': line.price_unit,
        #             # 'name': line.product_id.get_product_multiline_description_sale(),
        #             'name': line.name,
        #             'helpdesk_custom_line_id': line.id,
        #         }))
        # action['context'] = {
        #     'default_partner_id': self.partner_id.id,
        #     'default_order_line': line_list,
        #     'default_helpdesk_custom_ticket_id': self.id,
        #     'default_origin': self.name
        # }

        sale_order_id = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'helpdesk_custom_ticket_id': self.id,
            'origin': self.name,
        })

        for line in self.support_sale_line_ids:
            if not line.order_line_id:

                sale_order_id.write({'order_line': [(0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'product_uom': line.product_uom.id,
                        # 'price_unit': line.price_unit,
                        'name': line.name,
                        'helpdesk_custom_line_id': line.id
                        })]})
        action['domain'] = [('id','=',sale_order_id.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
