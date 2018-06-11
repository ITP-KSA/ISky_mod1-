from odoo import models, fields, api


class projectProjectInh(models.Model):
    _inherit = 'project.project'

    rfq_num = fields.Char("RFQ#")


class projectTaskInh(models.Model):
    _inherit = 'project.task'

    badge_number = fields.Text(string="Badge Number")
    contact_info = fields.Text(string="Contact Info")
    special_sale = fields.Boolean(string="Special Sale")

    line_item = fields.Char("Line Item #")

