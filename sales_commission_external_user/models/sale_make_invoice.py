# -*- coding: utf-8 -*-
#from openerp import models, fields, api
from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    #@api.multi
    # def _create_invoice(self, order, so_line, amount):
    def _create_invoices(self, sale_orders):
        #invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order=order,so_line=so_line,amount=amount)
        invoice = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
        if invoice:
            # if order.sale_commission_user_ids:
            # if sale_orders.sale_commission_user_ids:
            #     sale_commission_user_lines = []
            #     # for commission in order.sale_commission_user_ids:
            #     for commission in sale_orders.sale_commission_user_ids:
            #         sale_commission_user_lines.append((0, 0, {
            #             'level_id': commission.level_id.id,
            #             'user_id': commission.user_id and commission.user_id.id or False}))
            #     invoice.write({'sale_commission_user_ids': sale_commission_user_lines})
    
            # # if order.sale_commission_percentage_ids:
            # if sale_orders.sale_commission_percentage_ids:
            #     sale_commission_lines = []
            #     # for commission in order.sale_commission_percentage_ids:
            #     for commission in sale_orders.sale_commission_percentage_ids:
            #         sale_commission_lines.append((0, 0, {
            #             'level_id': commission.level_id.id,
            #             'percentage': commission.percentage}))
            #     invoice.write({'sale_commission_percentage_ids': sale_commission_lines})
            for line in invoice.invoice_line_ids:
                #line._onchange_product_id()
#                commission_based_on = self.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on') #odoo11#downpaymnt fix
                commission_based_on = line.company_id.commission_based_on
                if commission_based_on:
                    sale_commission_percentage = []
                    if commission_based_on == 'product_category':
                        for level in line.product_id.categ_id.sale_commission_percentage_ids:
                            sale_commission_percentage.append(level.id)
                    elif commission_based_on == 'product_template':
                        for level in line.product_id.sale_commission_percentage_ids:
                            sale_commission_percentage.append(level.id)
                    line.commission_percentage_ids = [(6, 0,sale_commission_percentage)]
        return invoice
