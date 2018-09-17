# -*- coding: utf-8 -*-
from odoo import models, fields


class ReceiveProducts(models.TransientModel):
    _name = "receive.products"

    product_id = fields.Many2one
