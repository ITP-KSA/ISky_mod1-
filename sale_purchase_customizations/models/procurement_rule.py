# -*- coding: utf-8 -*-
from odoo import api, models


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
        res.update({'product_qty': product_qty})
        return res

    @api.multi
    def _prepare_purchase_order_line(self, product_id,
                                     product_qty, product_uom,
                                     values, po, supplier):
        res = super(ProcurementRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier)
        import pdb
        pdb.set_trace()
        # res.update({'product_qty': product_qty})
        return res
