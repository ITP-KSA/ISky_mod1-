# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = "res.users"


    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouses")


    @api.onchange('company_id','company_ids')
    def onchange_company_ids(self):
        for rec in self:
            if rec.company_id or rec.company_ids:
                rec.warehouse_ids = ''