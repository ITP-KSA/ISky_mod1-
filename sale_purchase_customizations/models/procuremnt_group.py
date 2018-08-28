# -*- coding: utf-8 -*-
from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _get_rule(self, product_id, location_id, values):
        result = super(ProcurementGroup, self.with_context(
            {'location_id': location_id}))._get_rule(
            product_id, location_id, values)
        sale_line_rec = self.env['sale.order.line'].browse(
            [values.get('sale_line_id')])
        qty = self._context.get(str(product_id.id))
        result._run_buy(
            sale_line_rec.product_id, qty,
            sale_line_rec.product_uom, location_id, sale_line_rec.name,
            sale_line_rec.order_id.name, values)
        return result
