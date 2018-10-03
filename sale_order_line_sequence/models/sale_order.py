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
            sale_line_recs = self.env['sale.order.line'].search(
                [('order_id', '=', sale_order.id)])
            if not sale_line_recs:
                sale_order_id = self._context.get('params')
                if sale_order_id:
                    sale_order_id = sale_order_id.get('id')
                if sale_order_id and sale_order.name != 'New':
                    sale_line_recs = self.env['sale.order.line'].search(
                        [('order_id', '=', sale_order_id)])
            if not sale_line_recs:
                sequence = (max(sale_order.mapped(
                    'order_line.line_item') or [0]) + 1)
            if sale_line_recs:
                sequence_1 = (max(sale_order.mapped(
                    'order_line.line_item') or [0]) + 1)
                sequence_2 = max(sale_line_recs.mapped('line_item') or [0]) + 1
                sequence = max(sequence_2, sequence_1)
            sale_order.max_line_sequence = sequence

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_compute_max_line_sequence',
                                       store=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def create(self, vals):
        sol_rec = super(SaleOrderLine, self).create(vals)
        so_rec = sol_rec.order_id
        sol_rec.line_item = max(so_rec.order_line.mapped('line_item')) + 1
        return sol_rec
