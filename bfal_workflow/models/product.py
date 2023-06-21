# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

from logging import warning as w

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('project_id', 'project_template_id')
    def _check_project_and_template(self):
        w(">>> _check_project_and_template")
        pass

    @api.model
    def default_get(self, default_fields):
        res = super(ProductTemplate, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'division_id' : self.env.user.branch_id.division_id.id or False
            })
        return res

    division_id = fields.Many2one('division', string="Division")