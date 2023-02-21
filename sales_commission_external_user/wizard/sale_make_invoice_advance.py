# -*- coding: utf-8 -*-

from odoo import api, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if invoice:
            for line in invoice.invoice_line_ids:
                line._onchange_product_id()
        return invoice
