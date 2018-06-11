# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = "res.users"


    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouses")