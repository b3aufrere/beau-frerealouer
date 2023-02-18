# -*- coding: utf-8 -*-


from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
   
    helpdesk_custom_ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string='Helpdesk Ticket',
        states={'draft': [('readonly', False)]},
        copy=False,
    )

class SaleOrder(models.Model):
    _inherit = 'sale.order'
   
    helpdesk_custom_ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string='Helpdesk Ticket',
        copy=False,
    )

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({'helpdesk_custom_ticket_id': self.helpdesk_custom_ticket_id.id})
        return result

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    # def _create_invoice(self, order, so_line, amount):
    #     res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
    def _create_invoices(self, sale_orders):
        res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
        # res.helpdesk_custom_ticket_id = order.helpdesk_custom_ticket_id
        res.helpdesk_custom_ticket_id = sale_orders.helpdesk_custom_ticket_id
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    helpdesk_custom_line_id = fields.Many2one(
        'support.sales.line.custom',
        string="Helpdesk Line",
        copy=False,
        # readonly=True
    )

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if vals.get('helpdesk_custom_line_id'):
            helpdesk_custom_line_id = res.helpdesk_custom_line_id
            helpdesk_custom_line_id.order_line_id = res.id
            helpdesk_custom_line_id.order_id = res.order_id.id
        return res