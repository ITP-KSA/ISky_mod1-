# -*- coding: utf-8 -*-
import mimetypes
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Sale(models.Model):
    _inherit = "sale.order"

    print_and_pack = fields.Boolean(string="Print and Pack")
    ppa_document = fields.Binary(string="File")
    file_name = fields.Char()

    @api.onchange('file_name')
    def get_mimetype(self):
        for res in self:
            if res.file_name:
                res.mime_type = mimetypes.guess_type(res.file_name)

    @api.onchange('print_and_pack')
    def _onchange_print_pack(self):
        if self.sample:
            self.sample = False

    @api.onchange('sample')
    def _onchange_sample(self):
        if self.print_and_pack:
            self.print_and_pack = False

    @api.multi
    def create_print_and_pack(self):
        print_pack = self.env['print.pack']
        print_pack_rec = False
        for order in self:
            stock_product_lines = order.order_line.filtered(
                lambda o: o.product_id.type == 'product')
            for line in stock_product_lines:
                product_rec = line.product_id
                company_rec = self.env.user.company_id
                suppliers = product_rec.seller_ids
                supplier = suppliers[:1]
                if not supplier and not print_pack_rec:
                    raise UserError(_('''No any supplier
                        for product "%s"!''') % line.product_id.name)
                print_pack_rec = print_pack.search(
                    [('sale_order_id', '=', order.id),
                     ('partner_id', '=', supplier.name.id)])
                if print_pack_rec:
                    print_pack_rec = print_pack_rec[:1]
                if not print_pack_rec:
                    vals = {
                        'partner_id': supplier.name.id,
                        'sale_order_id': order.id,
                        'company_id': company_rec.id,
                        'date_planned': datetime.now(),
                        'ppa_document': order.ppa_document,
                        'file_name': order.file_name
                    }
                    print_pack_rec = print_pack.create(vals)
                vals = self._create_print_order_line(
                    print_pack_rec, line)
                self.env['ppa.lines'].sudo().create(vals)
                self.with_context(ppa_rec=print_pack_rec.id)
        return print_pack_rec

    @api.multi
    def _create_print_order_line(self, print_pack_rec, so_line):
        product_rec = so_line.product_id
        supplier = product_rec.seller_ids[:1]
        product_lang = product_rec.with_context({
            'lang': supplier.name.lang,
            'partner_id': supplier.name.id,
        })
        name = product_lang.display_name
        date_planned = datetime.utcnow().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        return {
            'name': name,
            'date_planned': date_planned,
            'product_qty': so_line.product_uom_qty,
            'product_id': product_rec.id,
            'product_uom': product_rec.uom_po_id.id,
            'price_unit': product_rec.standard_price,
            'order_id': print_pack_rec.id,
        }

    @api.multi
    def action_confirm(self):
        for order in self:
            res = {}
            if not self._context.get('printing') and order.print_and_pack:
                status = self.env.user.has_group(
                    'sales_team.group_sale_manager')
                if status:
                    self.create_print_and_pack()
                    self.check_before_confirm()
                    self.write(
                        {'state': 'pack',
                         'confirmation_date': fields.Datetime.now()
                         })
                else:
                    res = super(Sale, order).action_confirm()
            else:
                res = super(Sale, order).action_confirm()
        return res
