# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SupportSalesLineCustom(models.Model):
    _name = "support.sales.line.custom"
    _description = "Support Sales Order Line"
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    name = fields.Text(
        string='Description'
    )
    price_unit = fields.Float(
        string='Unit Price',
        digits='Product Price',
    )
    quantity = fields.Float(
        string='Quantity',
        digits='Product Unit of Measure',
        required=True,
        default=1
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
    )
    help_support_id = fields.Many2one(
        'helpdesk.ticket',
        string='Support Ticket',
    )
    order_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        readonly=True,
        copy=False,
    )
    order_line_id = fields.Many2one(
        'sale.order.line',
        string="Order Line",
        readonly=True,
        copy=False,
    )
    
    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            if rec.product_id.description_sale:
                rec.name = rec.product_id.description_sale
            else:
                rec.name = rec.product_id.name
            # rec.price_unit = rec.product_id.lst_price
            rec.product_uom = rec.product_id.uom_id.id
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
