# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.tools.float_utils import float_compare


class PPALines(models.Model):
    _name = "ppa.lines"
    _inherit = "purchase.order.line"

    name = fields.Text(string='Description', required=False)
    order_id = fields.Many2one("print.pack", string="PPA Order")
    ppa_invoice_lines = fields.One2many(
        'account.invoice.line', 'ppa_order_line_id', string="Bill Lines",
        readonly=True, copy=False)

    @api.multi
    def _create_ppa_stock_moves(self, picking, product_ids={}):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            for val in line._prepare_stock_moves(picking):
                for product_id in product_ids:
                    if product_id.id == val['product_id']:
                        product = self.env['product.product'].search(
                            [('product_tmpl_id', '=',
                                product_ids[product_id])])
                        val.update({'product_id': product.id})
                done += moves.create(val)
        return done

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line.
        This function returns a list of dictionary ready to be
        used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.move_ids.filtered(
                lambda x: x.state != 'cancel' and
                not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(
                move.product_uom_qty, self.product_uom,
                rounding_method='HALF-UP')
        template = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'ppa_line_id': self.id,
            'product_uom_qty': self.product_qty,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': picking.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0,
                         precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if self.product_uom.id != quant_uom.id and \
                    get_param('stock.propagate_uom') != '1':
                template['product_uom'] = quant_uom.id
            res.append(template)
        return res
