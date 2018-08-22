# -*- coding: utf-8 -*-
from odoo import models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _update_purchase_order_line(self, product_id,
                                    product_qty, product_uom,
                                    values, line, partner):
        return super(ProcurementRule, self)._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner)
