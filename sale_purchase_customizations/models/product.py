# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('default_code', operator, name),
                  ('name', operator, name),
                  ('product_part', operator, name),
                  ('product_mfr', operator, name),
                  ('product_mfr_name', operator, name),
                  ('product_material_code', operator, name),
                  ('product_smacc_code', operator, name),
                  ('product_samj_code', operator, name),
                  ]
        if domain:
            domain = ['|'] * 6 + domain
        tmpl_recs = self.env['product.template'].search(
            domain + args, limit=limit)
        product = self.search([('product_tmpl_id', 'in', tmpl_recs.ids)])
        recs = self.search(domain + args, limit=limit)
        ids = product.ids + recs.ids
        recs = self.browse(ids)
        return recs.name_get()

    product_part = fields.Char(string="Part")
    product_mfr = fields.Char(string="MFR")
    product_mfr_name = fields.Char(string="MFR Name")
    product_material_code = fields.Char(string="Material Code")
    product_smacc_code = fields.Char(string="SMACC Code")
    product_samj_code = fields.Char(string="SAMJ Code")

    @api.constrains('product_smacc_code')
    def _unquie_smacc_code(self):
        product_ids = len(self.search(
            [('product_smacc_code', '=', self.product_smacc_code)]))
        product_temp_ids = len(self.env['product.template'].search(
            [('product_smacc_code', '=', self.product_smacc_code)]))
        if product_ids > 1 and self.product_smacc_code:
            raise UserError("The SMACC CODE must be unique!")
        if product_temp_ids and self.product_smacc_code:
            raise UserError("The SMACC CODE must be unique!")
        return True

    @api.constrains('product_samj_code')
    def _unquie_product_samj_code(self):
        product_ids = len(self.search(
            [('product_samj_code', '=', self.product_samj_code)]))
        product_temp_ids = len(self.env['product.template'].search(
            [('product_samj_code', '=', self.product_samj_code)]))
        if product_temp_ids and self.product_samj_code:
            raise UserError("The SAMJ CODE must be unique!")
        if product_ids > 1 and self.product_samj_code:
            raise UserError("The SAMJ CODE must be unique!")
        return True


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_part = fields.Char(string="Part")
    product_mfr = fields.Char(string="MFR")
    product_mfr_name = fields.Char(string="MFR Name")
    product_material_code = fields.Char(string="Material Code")
    product_smacc_code = fields.Char(string="SMACC Code")
    product_samj_code = fields.Char(string="SAMJ Code")

    @api.constrains('product_smacc_code')
    def _unquie_smacc_code(self):
        product_temp_ids = len(self.search(
            [('product_smacc_code', '=', self.product_smacc_code)]))
        product_ids = len(self.env['product.product'].search(
            [('product_smacc_code', '=', self.product_smacc_code)]))
        if product_ids and self.product_smacc_code:
            raise UserError("The SMACC CODE must be unique!")
        if product_temp_ids > 1 and self.product_smacc_code:
            raise UserError("The SMACC CODE must be unique!")
        return True

    @api.constrains('product_samj_code')
    def _unquie_product_samj_code(self):
        product_temp_ids = len(self.search(
            [('product_samj_code', '=', self.product_samj_code)]))
        product_ids = len(self.env['product.product'].search(
            [('product_samj_code', '=', self.product_samj_code)]))
        if product_temp_ids > 1 and self.product_samj_code:
            raise UserError("The SAMJ CODE must be unique!")
        if product_ids and self.product_samj_code:
            raise UserError("The SAMJ CODE must be unique!")
        return True
