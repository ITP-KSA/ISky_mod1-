# -*- coding: utf-8 -*-
from odoo import api, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _update_purchase_order_line(self, product_id,
                                    product_qty, product_uom,
                                    values, line, partner):
        res = super(ProcurementRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner)
        exception_moves = self.env['stock.move'].search(
            [('procure_method', '=', 'make_to_stock'),
             ('product_id', '=', product_id.id),
             ('state', 'not in', ('cancel', 'done', 'draft'))])
        reserved_product_quantity = sum(
            [exception_move.product_uom_qty
             for
             exception_move
             in
             exception_moves])
        product_qty = self._context.get(
            str(product_id.id)) - reserved_product_quantity
        if product_qty < 0:
            product_qty = -product_qty
        res.update({'product_qty': product_qty})
        return res

    @api.multi
    def _prepare_purchase_order_line(self, product_id,
                                     product_qty, product_uom,
                                     values, po, supplier):
        res = super(ProcurementRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier)
        exception_moves = self.env['stock.move'].search(
            [('procure_method', '=', 'make_to_stock'),
             ('product_id', '=', product_id.id),
             ('state', 'not in', ('cancel', 'done', 'draft'))])
        reserved_product_quantity = sum(
            [exception_move.product_uom_qty
             for
             exception_move
             in
             exception_moves])
        product_qty = self._context.get(
            str(product_id.id)) - reserved_product_quantity
        if product_qty < 0:
            product_qty = -product_qty
        res.update({'product_qty': product_qty})
        return res
