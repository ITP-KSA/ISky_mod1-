# -*- coding: utf-8 -*-
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def create(self, vals):
        sol_rec = super(SaleOrderLine, self).create(vals)
        so_rec = sol_rec.order_id
        sol_rec.line_item = max(so_rec.order_line.mapped('line_item')) + 1
        return sol_rec
