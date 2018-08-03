# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, models, fields, SUPERUSER_ID


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sample = fields.Boolean(string="Is a Sample")
    date_return = fields.Date(string="Return Date")
    sample_state = fields.Selection([('sample', 'Sample'),
                                     ('sample_sent', 'Sample Sent'),
                                     ('sample_order', 'Sample Order'),
                                     ('cancel', 'Cancelled')],
                                    readonly=True, copy=False,
                                    index=True, track_visibility='onchange',
                                    default='sample')

    @api.multi
    def _action_confirm(self):
        status = super(SaleOrder, self)._action_confirm()
        for order_rec in self:
            if order_rec.sample:
                if order_rec.state == 'sent':
                    order_rec.write({'sample_state': 'sample_sent'})
                else:
                    order_rec.write({'sample_state': 'sample_order'})
        return status

    @api.multi
    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])
        orders.write({
            'sample_state': 'sample',
        })
        return super(SaleOrder, self).action_draft()

    @api.multi
    def action_cancel(self):
        self.write({'sample_state': 'cancel'})
        return super(SaleOrder, self).action_cancel()

    def return_mail_saleperson(self):
        cur_date = str(datetime.now().date().strftime('%m-%d-%Y'))
        sale_recs = self.search([('sample', '=', True),
                                 ('date_return', '=', cur_date)])
        admin_user_rec = self.env['res.users'].browse([SUPERUSER_ID])
        for sale_rec in sale_recs:
            template = self.env.ref(
                'product_sample.product_sample_data_email')
            ctx = self.env.context.copy()
            message = '''It's time to receive back sample %s.
                        Would you please check with customer?'''% sale_rec.name
            ctx.update({'body': message,
                        'email_to': sale_rec.user_id.email,
                        'email_from': admin_user_rec.email
                        })
            template.with_context(ctx).send_mail(
                sale_rec.id, force_send=True)
