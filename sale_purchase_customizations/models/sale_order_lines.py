from odoo import models, fields, api


class SalesOrderLines(models.Model):
    _inherit = 'sale.order.line'

    product_part = fields.Char(string="Part", related="product_id.product_part")
    product_mfr = fields.Char(string="MFR", related="product_id.product_mfr")
    product_mfr_name = fields.Char(string="MFR Name", related="product_id.product_mfr_name")
    product_material_code = fields.Char(string="Material Code", related="product_id.product_material_code")
    product_smacc_code = fields.Char(string="SMACC Code", related="product_id.product_smacc_code")
    product_samj_code = fields.Char(string="SAMJ Code", related="product_id.product_samj_code")

    line_item = fields.Char("Line Item #")

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SalesOrderLines, self)._prepare_invoice_line(qty)
        res.update({'line_item': self.line_item})
        return res

