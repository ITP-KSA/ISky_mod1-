# -*- coding: utf-8 -*-
from odoo import models


class ProcuremnetRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, values, group_id):
        res = super(ProcuremnetRule, self)._get_stock_move_values(
            product_id, product_qty, product_uom,
            location_id, name, origin, values, group_id)
        if self._context.get('print_pack'):
            location_id = self._context.get(
                'print_pack_rec').partner_id.property_stock_supplier.id
            res.update({'location_dest_id': location_id})
        return res
