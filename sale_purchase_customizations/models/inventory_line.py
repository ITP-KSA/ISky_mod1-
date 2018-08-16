# -*- coding: utf-8 -*-
from odoo import models, fields


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    product_smacc_code = fields.Char(string="SMACC Code",
                                     related="product_id.product_smacc_code")
    product_samj_code = fields.Char(string="SAMJ Code",
                                    related="product_id.product_samj_code")
