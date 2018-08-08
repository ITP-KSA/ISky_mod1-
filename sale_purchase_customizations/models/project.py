from odoo import models, fields, api, _


class projectProjectInh(models.Model):
    _inherit = 'project.project'

    rfq_num = fields.Char("RFQ#")
    privacy_visibility = fields.Selection([
            ('followers', _('On invitation only')),
            ('employees', _('Visible by all employees')),
            ('portal', _('Visible by following customers')),
        ],
        string='Privacy', required=True,
        default='followers',
        help="Holds visibility of the tasks or issues that belong to the current project:\n"
                "- On invitation only: Employees may only see the followed project, tasks or issues\n"
                "- Visible by all employees: Employees may see all project, tasks or issues\n"
                "- Visible by following customers: employees see everything;\n"
                "   if website is activated, portal users may see project, tasks or issues followed by\n"
                "   them or by someone of their company\n")


class projectTaskInh(models.Model):
    _inherit = 'project.task'

    badge_number = fields.Text(string="Badge Number", auto_join=True)
    contact_info = fields.Text(string="Contact Info", auto_join=True)
    special_sale = fields.Boolean(string="Special Sale", auto_join=True)
    
    line_item = fields.Char("Line Item #")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', '|', ('badge_number', operator, name),
                  ('contact_info', operator, name),
                  ('line_item', operator, name), ('name', operator, name)]
        if domain:
            domain = ['|'] + domain

        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
