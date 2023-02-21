# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # skip warning of Payment and Product/Product Category do not select together
#    @api.multi
    def set_values(self):
        ctx = self._context.copy()
        ctx.update(skip=True)
        super(ResConfigSettings, self.with_context(ctx)).set_values()
