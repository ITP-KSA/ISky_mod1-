# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    print_pack_id = fields.Many2one('print.pack', string="Print & Pack")

    def _prepare_invoice_line_from_ppa_line(self, line):
        if line.product_id.purchase_method == 'receive':
            qty = line.product_qty - line.qty_invoiced
        else:
            qty = line.qty_received - line.qty_invoiced
        if float_compare(
                qty, 0.0,
                precision_rounding=line.product_uom.rounding) <= 0:
            qty = 0.0
        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
        invoice_line = self.env['account.invoice.line']
        data = {
            'ppa_order_line_id': line.id,
            'name': line.order_id.name + ': ' + line.name,
            'origin': line.order_id.origin,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context(
                {'journal_id': self.journal_id.id,
                 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id.with_context(
                date=self.date_invoice).compute(
                line.price_unit, self.currency_id, round=False),
            'quantity': qty,
            'discount': 0.0,
            'account_analytic_id': line.account_analytic_id.id,
            'analytic_tag_ids': line.analytic_tag_ids.ids,
            'invoice_line_tax_ids': invoice_line_tax_ids.ids
        }
        account = invoice_line.get_invoice_line_account(
            'in_invoice', line.product_id,
            line.order_id.fiscal_position_id, self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data

    @api.onchange('print_pack_id')
    def _onchange_print_pack_id(self):
        if self.print_pack_id:
            self.purchase_id = False
        if not self.print_pack_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.print_pack_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        for line in self.print_pack_id.ppa_order_line - self.invoice_line_ids.mapped('ppa_order_line_id'):
            data = self._prepare_invoice_line_from_ppa_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids = new_lines
        self.payment_term_id = self.print_pack_id.payment_term_id
        self.env.context = dict(
            self.env.context, from_purchase_order_change=True)
        return {}

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if self.purchase_id:
            self.print_pack_id = False
        return super(AccountInvoice, self).purchase_order_change()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    ppa_order_line_id = fields.Many2one('ppa.lines',
                                        string="Print & Pack Order line",
                                        ondelete='set null', index=True,
                                        readonly=True)
    ppa_order_id = fields.Many2one('print.pack',
                                   related='ppa_order_line_id.order_id',
                                   string='Pack Order', store=False,
                                   readonly=True, related_sudo=False)
