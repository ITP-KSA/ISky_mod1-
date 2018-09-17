# -*- coding: utf-8 -*-
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    ppa_line_id = fields.Many2one('ppa.lines', string="Print and pack Lines")
