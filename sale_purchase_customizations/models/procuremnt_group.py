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
        if qty:
            exception_moves = self.env['stock.move'].search(
                [('procure_method', '=', 'make_to_order'),
                 ('product_id', '=', product_id.id),
                 ('state', 'not in', ('cancel', 'done', 'draft'))])
            reserved_product_quantity = sum(
                [exception_move.product_uom_qty
                 for
                 exception_move
                 in
                 exception_moves])
            qty -= reserved_product_quantity
            if qty < 0:
                qty = -qty
            type_obj = self.env['stock.picking.type']
            company_id = self.env.context.get(
                'company_id') or self.env.user.company_id.id
            types = type_obj.search(
                [('code', '=', 'incoming'),
                 ('warehouse_id.company_id', '=', company_id)])
            if not types:
                types = type_obj.search(
                    [('code', '=', 'incoming'),
                     ('warehouse_id', '=', False)])
            po_location_id = types[:1].default_location_dest_id
            print("location", po_location_id)
            po_values = sale_line_rec._prepare_procurement_values(
                group_id=sale_line_rec.order_id.procurement_group_id)
            result._run_buy(
                sale_line_rec.product_id, qty,
                sale_line_rec.product_uom, po_location_id, sale_line_rec.name,
                sale_line_rec.order_id.name, po_values)
        return result
