# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    badge_number = fields.Text(string="Badge Number")
    contact_info = fields.Text(string="Contact Info")
    special_sale = fields.Boolean(
        string="Special Sale", related='order_id.special_sale', store=True)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    special_sale = fields.Boolean(string="Special Sale", default=True)
    client_po = fields.Char(string="Client's P.O")
    project_id = fields.Many2one('project.project')
    rfq_num = fields.Char("RFQ#")

    @api.model
    def create(self, vals):
        if vals.get('special_sale') and not vals.get('project_id'):
            raise ValidationError("Please select project")
        return super(SaleOrder, self).create(vals)

    @api.multi
    def check_before_confirm(self):
        self.ensure_one()
        parent = False
        project = False
        if self.special_sale:
            # Step#1: Add Client PO as task in the project already selected by
            # the user
            rfq_num = self.rfq_num
            if not self.rfq_num:
                rfq_num = ''
            task = self.env['project.task'].sudo().create({
                'name': self.partner_id.name + "-" + rfq_num,
                'project_id': self.project_id.id,
                'sale_order_id': self.id,
                'partner_id': self.partner_id.id,
            })
            parent = task.id
            project = self.project_id
        else:
            # Step#1: create new project with Name of the client and S.O.#
            if self.client_po:
                client_po = self.client_po
            else:
                client_po = ''
            project = self.env['project.project'].sudo().create({
                'name': client_po + "-" + self.name,
                'rfq_num': self.rfq_num,
            })
            project.task_ids = False
        # Step#2: For each line in the order lines (having service products)
        # create a task in the above created project
        for line in self.order_line:
            sub_task = self.env['project.task'].sudo().create({
                'name': line.product_id.name,
                'project_id': project.id,
                'partner_id': self.partner_id.id,
                'parent_id': parent,
                'contact_info': line.contact_info,
                'badge_number': line.badge_number,
                'special_sale': line.special_sale,
                'line_item': line.line_item
            })

            sub_task.sale_line_id = line.id

    def create_po_from_so(self, s_order):
        purchase = self.env['purchase.order']
        for line in s_order.order_line:
            product_rec = line.product_id
            company_rec = self.env.user.company_id
            if line.product_id.type in ('product'):
                suppliers = product_rec.seller_ids
                supplier = suppliers[:1]
                type_obj = self.env['stock.picking.type']
                types = type_obj.search(
                    [('code', '=', 'incoming'),
                     ('warehouse_id.company_id', '=', company_rec.id)])
                if not types:
                    types = type_obj.search(
                        [('code', '=', 'incoming'),
                         ('warehouse_id', '=', False)])
                exception_moves = self.env['stock.move'].search(
                    [('procure_method', '=', 'make_to_order'),
                     ('product_id', '=', line.product_id.id),
                     ('state', 'not in', ('cancel', 'done', 'draft'))])
                for move in exception_moves:
                    origin = (move.group_id and (move.group_id.name + ":") or "") + (
                        move.rule_id and move.rule_id.name or move.origin or move.picking_id.name or "/")
                if not exception_moves:
                    origin = line.order_id.name
                purchase_rec = purchase.search(
                    [('partner_id', '=', supplier.name.id),
                     ('state', 'in', ['draft', 'sent']),
                     ('picking_type_id', '=', types[:1].id),
                     ('company_id', '=', company_rec.id)])
                if purchase_rec:
                    purchase_rec = purchase_rec[:1]
                if not purchase_rec:
                    fpos = self.env['account.fiscal.position'].with_context(
                        force_company=company_rec.id).get_fiscal_position(
                        supplier.name.id)
                    vals = {
                        'partner_id': supplier.name.id,
                        'picking_type_id': types[:1].id,
                        'origin': origin,
                        'company_id': company_rec.id,
                        'fiscal_position_id': fpos,
                    }
                    purchase_rec = purchase.create(vals)
                elif not purchase_rec.origin or origin not in \
                        purchase_rec.origin.split(', '):
                    if purchase_rec.origin:
                        if origin:
                            purchase_rec.write(
                                {'origin': purchase_rec.origin +
                                 ', ' + origin})
                        else:
                            purchase_rec.write({'origin': purchase_rec.origin})
                    else:
                        purchase_rec.write({'origin': origin})
                # Create Line
                purchase_line = False
                for po_line in purchase_rec.order_line:
                    if po_line.product_id.id == product_rec.id and po_line.product_uom == product_rec.uom_po_id:
                        vals = self.update_po_line(
                            po_line, supplier, company_rec,
                            line)
                        purchase_line = po_line.write(vals)
                        break
                if not purchase_line:
                    vals = self._create_purchase_order_line(
                        purchase_rec, product_rec, company_rec, line)
                    if vals.get('product_qty') > 0:
                        self.env['purchase.order.line'].sudo().create(vals)
                if not purchase_rec.order_line:
                    purchase_rec.unlink()

    def update_po_line(self, line, seller, company_rec, so_line):
        qty_to_purchase = self.get_quantity(so_line)
        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            seller.price, line.product_id.supplier_taxes_id, line.taxes_id,
            company_rec) if seller else 0.0
        return {
            'product_qty': qty_to_purchase,
            'price_unit': price_unit,
        }

    def _create_purchase_order_line(self, purchase_rec,
                                    product_rec, company_rec, line):
        supplier = product_rec.seller_ids[:1]
        qty_to_purchase = self.get_quantity(line)
        seller = product_rec._select_seller(
            partner_id=supplier.name,
            quantity=qty_to_purchase,
            date=purchase_rec.date_order and purchase_rec.date_order[:10],
            uom_id=product_rec.uom_po_id)
        taxes = product_rec.supplier_taxes_id
        fpos = purchase_rec.fiscal_position_id
        taxes_id = fpos.map_tax(taxes) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(
                lambda x: x.company_id.id == company_rec.id)
        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            seller.price, product_rec.supplier_taxes_id,
            taxes_id, company_rec) if seller else 0.0
        date_planned = self.env['purchase.order.line']._get_date_planned(
            seller, po=purchase_rec).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        product_lang = product_rec.with_context({
            'lang': supplier.name.lang,
            'partner_id': supplier.name.id,
        })
        name = product_lang.display_name
        return {
            'name': name,
            'product_qty': qty_to_purchase,
            'product_id': product_rec.id,
            'product_uom': product_rec.uom_po_id.id,
            'price_unit': price_unit,
            'date_planned': date_planned,
            'taxes_id': [(6, 0, taxes_id.ids)],
            'order_id': purchase_rec.id,
        }

    def get_quantity(self, so_line):
        exception_moves = self.env['stock.move'].search(
            [('product_id', '=', so_line.product_id.id),
             ('state', 'not in', ('cancel', 'done', 'draft'))])
        sale_pickings = exception_moves.filtered(
            lambda em: em.picking_id.sale_id)
        purchase_pickings = exception_moves.filtered(
            lambda em: em.picking_id.purchase_id)
        so_reserved_product_quantity = sum(
            [exception_move.product_uom_qty
             for
             exception_move
             in
             sale_pickings])
        po_reserved_product_quantity = sum(
            [exception_move.product_uom_qty
             for
             exception_move
             in
             purchase_pickings])
        if not po_reserved_product_quantity:
            if so_reserved_product_quantity < so_line.product_id.qty_available:
                qty = 0
            else:
                qty = so_reserved_product_quantity - \
                    so_line.product_id.qty_available
        else:
            qty = so_reserved_product_quantity - \
                po_reserved_product_quantity - \
                so_line.product_id.qty_available
        if qty < 0:
            qty = -qty
        return qty

    @api.multi
    def action_confirm(self):
        for order in self:
            order.write({'client_po': order.rfq_num})
            status = self.env.user.has_group('sales_team.group_sale_manager')
            res = super(SaleOrder, order).action_confirm()
            self.create_po_from_so(order)
            if res:
                if not status:
                    if order.state in ['sale', 'sent']:
                        order.state = 'approve'
                if status:
                    order.check_before_confirm()
                for picking in order.picking_ids:
                    if not picking.client_po:
                        picking.client_po = order.client_po
        return True

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['client_po'] = self.client_po
        res['rfq_num'] = self.rfq_num
        return res

    @api.multi
    def action_approve_quotation(self):
        for order in self:
            order.action_confirm()
        return True

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            task_rec = self.env['project.task'].search(
                [('sale_order_id', '=', order.id)])
            client_po = ''
            if order.client_po:
                client_po = order.client_po
            name = order.partner_id.name + "-" + client_po
            task_rec.write({'name': name})
        return res
