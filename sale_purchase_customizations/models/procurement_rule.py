# -*- coding: utf-8 -*-
from odoo import models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _make_po_get_domain(self, values, partner):
        domain = super(ProcurementRule, self)._make_po_get_domain(
            values, partner)
        tuplex = list(domain)
        for x in tuplex:
            if (x[0] == 'group_id'):
                tuplex.pop(tuplex.index(x))
        domain = tuple(tuplex)
        return domain

    def _update_purchase_order_line(self, product_id,
                                    product_qty, product_uom,
                                    values, line, partner):
        res = super(ProcurementRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner)
        product_uom = line.product_id.uom_id
        sale_line_rec = self.env['sale.order.line'].browse(
            [values.get('sale_line_id')])
        procurement_uom_po_qty = product_uom._compute_quantity(
            sale_line_rec.product_uom_qty, product_id.uom_po_id)
        product_qty = line.product_qty + procurement_uom_po_qty
        res.update({'product_qty': product_qty})
        return res
