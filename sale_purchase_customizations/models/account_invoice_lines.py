from odoo import models, fields, api


class InvLines(models.Model):
    _inherit = 'account.invoice.line'

    product_part = fields.Char(string="Part", related="product_id.product_part")
    product_mfr = fields.Char(string="MFR", related="product_id.product_mfr")
    product_mfr_name = fields.Char(string="MFR Name", related="product_id.product_mfr_name")
    product_material_code = fields.Char(string="Material Code", related="product_id.product_material_code")
    product_smacc_code = fields.Char(string="SMACC Code", related="product_id.product_smacc_code")
    product_samj_code = fields.Char(string="SAMJ Code", related="product_id.product_samj_code")

    line_item = fields.Char("Line Item #")

