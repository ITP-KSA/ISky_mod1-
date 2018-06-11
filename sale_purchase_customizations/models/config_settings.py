from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_subtask_project = fields.Boolean("Sub-tasks", invisible=True, default=True)
    #
    # def set_values(self):
    #     set_param = self.env['ir.config_parameter'].set_param
    #     set_param('group_subtask_project', (True))
    #     super(ResConfigSettings, self).set_values()