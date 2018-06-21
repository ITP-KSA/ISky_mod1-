# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.depends('order_line')
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in invoice lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new invoice lines, the sequence is automatically
        added as :  max_sequence + 1
        """
        for sale_order in self:
            sale_order.max_line_sequence = (
                max(sale_order.mapped('order_line.line_item') or [0]) + 1)

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_compute_max_line_sequence',
                                       store=True)

    # @api.multi
    # def _reset_sequence(self):
    #     for rec in self:
    #         current_sequence = 1
    #         for line in rec.order_line:
    #             line.line_item = current_sequence
    #             current_sequence += 1
    #
    # @api.multi
    # def write(self, values):
    #     res = super(SaleOrder, self).write(values)
    #     self._reset_sequence()
    #     return res
