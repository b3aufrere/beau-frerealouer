from odoo import models, fields, api
from odoo.tools.misc import formatLang

from logging import warning as w

class AccountMove(models.Model):
    _inherit = "account.move"

    division_id = fields.Many2one('division', related='invoice_user_id.employee_id.branch_id.division_id', string='Division')
    # entreprise_id = fields.Many2one('entreprise', related='invoice_user_id.employee_id.entreprise_id', string='Entreprise')
    branch_id = fields.Many2one('res.branch', related='invoice_user_id.employee_id.branch_id', string="Entreprise")
    tip_value = fields.Monetary(
        string="Tip Amount", compute='_compute_amount', store=True, readonly=True,)

    amount_untaxed_display = fields.Monetary(
        string='Untaxed Amount',
        compute='_compute_amount', store=True, readonly=True,
    )

    def _get_name_invoice_report(self):
        self.ensure_one()
        
        return "bfal_workflow.report_invoice_document_bfal"
    
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state')
    def _compute_amount(self):
        for move in self:
            total_untaxed, total_untaxed_currency = 0.0, 0.0
            total_tax, total_tax_currency = 0.0, 0.0
            total_residual, total_residual_currency = 0.0, 0.0
            total, total_currency = 0.0, 0.0
            #
            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===
                    if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in ('product', 'rounding'):
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term':
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency
            tip_value = abs(sum(move.line_ids.filtered(lambda line: line.product_id.id ==
                            self.env.company.tip_product_id.id).mapped('amount_currency')))
            
            sign = move.direction_sign
            move.amount_untaxed = sign * total_untaxed_currency
            move.amount_tax = sign * total_tax_currency
            move.amount_total = sign * total_currency
            move.amount_residual = -sign * total_residual_currency
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(
                total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual
            move.amount_total_in_currency_signed = abs(
                move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)
            move.tip_value = tip_value
            move.amount_untaxed_display = sign * total_untaxed_currency - tip_value

    @api.model
    def _compute_tax_totals(self):
        w(">>> _compute_tax_totals")
        rec = super()._compute_tax_totals()
        for res in self:
            if res.tax_totals is not None:
                vals = res.tax_totals
                vals.update({
                    'amount_untaxed': vals['amount_untaxed'] - res.tip_value,
                    'tip_value': res.tip_value,
                    'formatted_tip_value': formatLang(self.env, res.tip_value, currency_obj=res.currency_id),
                    'formatted_amount_untaxed': formatLang(self.env, vals['amount_untaxed'] - res.tip_value, currency_obj=res.currency_id),
                })
                for data in vals.get('subtotals'):
                    w(">>> _compute_tax_totals 2")
                    if data.get('name') in ['Untaxed Amount', 'Montant HT']:
                        w(">>> _compute_tax_totals 3")
                        # data['amount'] -= res.tip_value
                        # value = data['amount']
                        # data['formatted_amount'] = formatLang(self.env, value, currency_obj=res.currency_id),

                        w(f"amount_untaxed >>> {res.amount_untaxed}")
                        w(f"tip_value >>> {res.tip_value}")
                        w(f"amount_untaxed_display >>> {res.amount_untaxed_display}")
                
                        data['formatted_amount'] = formatLang(self.env, res.amount_untaxed - res.tip_value, currency_obj=res.currency_id),
                res.tax_totals = vals
        return rec