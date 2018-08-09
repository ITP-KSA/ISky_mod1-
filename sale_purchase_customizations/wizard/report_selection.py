# -*- coding: utf-8 -*-
from odoo import api, models


class ReportSelection(models.TransientModel):
    _name = "report.selection"

    @api.multi
    def print_ai_joud_quo_report(self):
        active_ids = self._context.get('active_ids')
        order_recs = self.env['sale.order'].browse(active_ids)
        return self.env.ref('sale_purchase_customizations.mawaten_aljoudwiht_quotation').report_action(order_recs)

    @api.multi
    def print_quotation_report(self):
        active_ids = self._context.get('active_ids')
        order_recs = self.env['sale.order'].browse(active_ids)
        order_recs.filtered(lambda s: s.state ==
                            'draft').write({'state': 'sent'})
        return self.env.ref('sale.action_report_saleorder').report_action(order_recs)

    @api.multi
    def print_invoice_report(self):
        active_ids = self._context.get('active_ids')
        inv_recs = self.env['account.invoice'].browse(active_ids)
        inv_recs.sent = True
        if self.user_has_groups('account.group_account_invoice'):
            return self.env.ref('account.account_invoices').report_action(inv_recs)
        else:
            return self.env.ref('account.account_invoices_without_payment').report_action(inv_recs)

    @api.multi
    def print_ai_joud_inv_report(self):
        active_ids = self._context.get('active_ids')
        inv_recs = self.env['account.invoice'].browse(active_ids)
        return self.env.ref('sale_purchase_customizations.mawaten_aljoudwiht_invoice').report_action(inv_recs)
