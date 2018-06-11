# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Picking(models.Model):
    _inherit = "stock.picking"

    client_po = fields.Char(string="Client's P.O")
