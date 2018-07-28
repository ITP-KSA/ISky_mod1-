# -*- coding: utf-8 -*-

from odoo import fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    client_po = fields.Char(string="Client's P.O")
