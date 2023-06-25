from odoo import api,fields,models

class ResCompany(models.Model):
	_inherit = 'res.company'

	tip_product_id = fields.Many2one('product.product', string='Tip Product')

class ResConfigSetting(models.TransientModel):
	_inherit = 'res.config.settings'

	tip_product_id = fields.Many2one(related="company_id.tip_product_id", string='Tip Product', store="True", readonly=False)