from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    division_id = fields.Many2one('division', related='invoice_user_id.employee_id.entreprise_id.division_id', string='Division')
    entreprise_id = fields.Many2one('entreprise', related='invoice_user_id.employee_id.entreprise_id', string='Entreprise')

    def _get_name_invoice_report(self):
        self.ensure_one()
        
        return "bfal_workflow.report_invoice_document_bfal"