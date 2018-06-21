from odoo import models, fields, api
from odoo.osv import expression


class projectProjectInh(models.Model):
    _inherit = 'project.project'

    rfq_num = fields.Char("RFQ#")


class projectTaskInh(models.Model):
    _inherit = 'project.task'

    badge_number = fields.Text(string="Badge Number", auto_join=True)
    contact_info = fields.Text(string="Contact Info" ,auto_join=True)
    special_sale = fields.Boolean(string="Special Sale",auto_join=True)

    line_item = fields.Char("Line Item #")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain =['|','|', ('badge_number', operator, name), ('contact_info', operator, name),
                 ('line_item', operator, name),('name', operator, name)]
        if domain:
            domain = ['|'] + domain

        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
