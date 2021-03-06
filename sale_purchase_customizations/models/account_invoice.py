# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    client_po = fields.Char(string="Client's P.O")
    rfq_num = fields.Char("RFQ#")
    product_id = fields.Many2one(
        'product.product', related="invoice_line_ids.product_id")
