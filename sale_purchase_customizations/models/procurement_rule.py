# -*- coding: utf-8 -*-
from odoo import api, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _update_purchase_order_line(self, product_id,
                                    product_qty, product_uom,
                                    values, line, partner):
        res = super(ProcurementRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner)
        product_qty = self._context.get(str(product_id.id))
        res.update({'product_qty': product_qty})
        return res

    @api.multi
    def _prepare_purchase_order_line(self, product_id,
                                     product_qty, product_uom,
                                     values, po, supplier):
        res = super(ProcurementRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier)
        product_qty = self._context.get(str(product_id.id))
        res.update({'product_qty': product_qty})
        return res
