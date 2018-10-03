from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesOrderLines(models.Model):
    _inherit = 'sale.order.line'

    product_part = fields.Char(
        string="Part", related="product_id.product_part")
    product_mfr = fields.Char(string="MFR", related="product_id.product_mfr")
    product_mfr_name = fields.Char(
        string="MFR Name", related="product_id.product_mfr_name")
    product_material_code = fields.Char(
        string="Material Code", related="product_id.product_material_code")
    product_smacc_code = fields.Char(
        string="SMACC Code", related="product_id.product_smacc_code")
    product_samj_code = fields.Char(
        string="SAMJ Code", related="product_id.product_samj_code")

    line_item = fields.Integer(
        string="Line Item #",
        help="Shows the sequence of this line in the sale order.")

    @api.multi
    @api.constrains('line_item')
    def _unique_line_item(self):
        for sol in self:
            line_item_list = sol.order_id.order_line.with_context(
                id1=sol.id).filtered(
                lambda l: l.id != l._context['id1']).mapped('line_item')
            if sol.line_item in line_item_list:
                raise ValidationError(
                    _("Line Item # must be unique per order!"))

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SalesOrderLines, self)._prepare_invoice_line(qty)
        res.update({'line_item': self.line_item})
        return res
