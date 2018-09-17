# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class PrintPack(models.Model):
    _name = "print.pack"
    _inherit = "purchase.order"

    name = fields.Char('Order Reference', required=True,
                       index=True, copy=False, default='New')
    sale_order_id = fields.Many2one("sale.order", string="Sale Order",
                                    domain="[('print_and_pack', '=', True)]")
    ppa_order_line = fields.One2many("ppa.lines", "order_id")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancel')],
                             string='Status', readonly=True, index=True,
                             copy=False, default='draft',
                             track_visibility='onchange')

    @api.depends('ppa_order_line.invoice_lines.invoice_id')
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.invoice']
            for line in order.ppa_order_line:
                invoices |= line.invoice_lines.mapped('invoice_id')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    @api.multi
    def action_view_ppa_invoice(self):
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice',
                             'default_print_pack_id': self.id}

        if not self.invoice_ids:
            # Choose a default account journal in the same currency in case a
            # new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env[
                'account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = self.invoice_ids[
                0].journal_id.id

        # choose the view_mode accordingly
        if len(self.invoice_ids) != 1:
            result['domain'] = "[('id', 'in', " + \
                str(self.invoice_ids.ids) + ")]"
        elif len(self.invoice_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result

    @api.multi
    def button_approve(self, product_ids, force=False):
        self.write(
            {'state': 'confirm',
             'date_approve': fields.Date.context_today(self)})
        self._create_picking_ppa()
        self.filtered(
            lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        return {}

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'print.pack') or _('New')
        return super(PrintPack, self).create(vals)

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    @api.multi
    def create_product(self, line):
        vals = {}
        if line.product_id.type == 'product':
            vals.update({
                'name': line.product_id.name + "_" +
                line.order_id.sale_order_id.name,
                'type': 'product',
                'sale_ok': True,
                'purchase_ok': True,
                'list_price': line.product_id.list_price
            })
        return vals

    @api.multi
    def insert_sale_order_lines(self, order_line, product_id):
        so_line = self.env['sale.order.line']
        vals = {
            'product_id': product_id.id,
            'order_id': order_line.order_id.id,
            'price_unit': product_id.list_price,
            'product_uom_qty': order_line.product_uom_qty,
            'name': order_line.name,
            'product_uom': order_line.product_uom.id,
        }
        so_line.create(vals)

    @api.multi
    def button_confirm(self):
        for order in self:
            product_ids = []
            if order.state not in ['draft']:
                continue
            product = self.env['product.template']
            for order_line in order.ppa_order_line:
                vals = self.create_product(order_line)
                product_rec = product.create(vals)
                vendor_location = order.partner_id.property_stock_supplier
                quant_rec = self.env['stock.quant'].search(
                    [('location_id', '=', vendor_location.id),
                     ('product_id', '=', order_line.product_id.id)])
                if quant_rec.quantity < order_line.product_qty:
                    raise UserError(_("Before confirm this order please \
                        maintain product stock."))
                product_id = self.env['product.product'].search(
                    [('product_tmpl_id', '=', product_rec.id)])
                self.env['product.supplierinfo'].create({
                    'name': order_line.order_id.partner_id.id,
                    'product_tmpl_id': product_rec.id,
                    'product_id': product_id.id})
                product_ids.append(product_rec.id)
                order_line = order.sale_order_id.order_line.with_context(
                    product_id=order_line.product_id.id).filtered(
                    lambda p: p.product_id.id == p._context['product_id'])
                self.insert_sale_order_lines(order_line, product_id)
                order_line.unlink()
            order.button_approve(product_ids)
        return True

    @api.multi
    def button_cancel(self):
        for order in self:
            for pick in order.picking_ids:
                if pick.state == 'done':
                    raise UserError(
                        _('Unable to cancel order %s as some receptions have \
                            already been done.') % (order.name))
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(
                        _("Unable to cancel this order. You must \
                            first cancel related vendor bills."))

            if order.state in ('draft'):
                for order_line in order.ppa_order_line:
                    if order_line.move_dest_ids:
                        siblings_states = (order_line.move_dest_ids.mapped(
                            'move_orig_ids')).mapped('state')
                        if all(state in ('done', 'cancel')
                               for state in siblings_states):
                            order_line.move_dest_ids.write(
                                {'procure_method': 'make_to_stock'})
                            order_line.move_dest_ids._recompute_state()

            for pick in order.picking_ids.filtered(
                    lambda r: r.state != 'cancel'):
                pick.action_cancel()

            order.ppa_order_line.write({'move_dest_ids': [(5, 0, 0)]})

        self.write({'state': 'cancel'})

    @api.multi
    def _create_picking_ppa(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.ppa_order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(
                    lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = order.ppa_order_line._create_ppa_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in (
                    'done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': picking,
                            'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True
