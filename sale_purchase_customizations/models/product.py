# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('default_code', operator, name), ('name', operator, name),
                  ('product_part', operator, name),
                  ('product_mfr', operator, name),
                  ('product_mfr_name', operator, name),
                  ('product_material_code', operator, name),
                  ('product_smacc_code', operator, name),
                  ('product_samj_code', operator, name),
                  ]
        if domain:
            domain = ['|'] * 6 + domain
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_part = fields.Char(string="Part")
    product_mfr = fields.Char(string="MFR")
    product_mfr_name = fields.Char(string="MFR Name")
    product_material_code = fields.Char(string="Material Code")
    product_smacc_code = fields.Char(string="SMACC Code")
    product_samj_code = fields.Char(string="SAMJ Code")
