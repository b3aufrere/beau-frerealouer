# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    branch_id = fields.Many2one('res.branch')

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.branch_id"