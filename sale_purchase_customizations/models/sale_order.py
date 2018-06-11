# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    badge_number = fields.Text(string="Badge Number")
    contact_info = fields.Text(string="Contact Info")
    special_sale = fields.Boolean(string="Special Sale", related='order_id.special_sale', store=True)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    special_sale = fields.Boolean(string="Special Sale")
    client_po = fields.Char(string="Client's P.O")
    project_id = fields.Many2one('project.project')
    rfq_num = fields.Char("RFQ#")



    @api.model
    def create(self, vals):
        if vals['special_sale'] and not vals['project_id']:
            raise ValidationError("Please select project")
        return super(SaleOrder, self).create(vals)

    @api.one
    def check_product_qty_available(self):
        '''
        Create purchase orders for order lines
        with ordered qty greater than the qty available.
        '''
        errors = []
        for line in self.order_line:
            if line.product_id.type in ('consu', 'product') and float_compare(line.product_id.qty_available,
                                                                              line.product_uom_qty,
                                                                              line.product_uom.rounding) < 0:
                if not line.order_id.procurement_group_id:
                    line.order_id.procurement_group_id = self.env['procurement.group'].create({
                        'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                        'sale_id': line.order_id.id,
                        'partner_id': line.order_id.partner_shipping_id.id,
                    })
                values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
                values.setdefault('company_id', self.env['res.company']._company_default_get('procurement.group'))
                values.setdefault('priority', '1')
                values.setdefault('date_planned', fields.Datetime.now())

                # keep dest address empty to deliver to your own company
                values.update({'partner_dest_id': False})

                # get dest location
                type_obj = self.env['stock.picking.type']
                company_id = self.env.context.get('company_id') or self.env.user.company_id.id
                types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
                if not types:
                    types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
                location_id = types[:1].default_location_dest_id

                rule = line.order_id.procurement_group_id._get_rule(line.product_id, location_id, values)
                if not rule:
                    raise UserError(_('No procurement rule found. Please verify the configuration of your routes'))

                qty_to_purchase = line.product_uom_qty - line.product_id.qty_available
                try:
                    rule._run_buy(line.product_id, qty_to_purchase, line.product_uom, location_id, line.name,
                                  line.order_id.name, values)
                except UserError as error:
                    errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def check_before_confirm(self):
        self.ensure_one()
        parent = False
        project = False
        if self.special_sale:
            # Step#1: Add Client PO as task in the project already selected by the user
            task = self.env['project.task'].sudo().create({
                'name': self.client_po,
                'project_id': self.project_id.id,
            })
            parent = task.id
            project = self.project_id
        else:
            # Step#1: create new project with Name of the client and S.O.#
            if self.client_po:
                client_po = self.client_po
            else:
                client_po = ''
            project = self.env['project.project'].create({
                'name': client_po + "-" + self.name,
                'rfq_num': self.rfq_num,
            })
            project.task_ids = False
        # Step#2: For each line in the order lines (having service products) create a task in the above created project
        for line in self.order_line:
            task = self.env['project.task'].sudo().create({
                'name': line.product_id.name,
                'project_id': project.id,
                'partner_id': self.partner_id.id,
                'parent_id': parent,
                'contact_info': line.contact_info,
                'badge_number': line.badge_number,
                'special_sale': line.special_sale,
                'line_item': line.line_item,
            })

            task.sale_line_id = line.id,

    @api.multi
    def action_confirm(self):
        for order in self:
            order.check_before_confirm()
            res = super(SaleOrder, order).action_confirm()
            order.check_product_qty_available()
            if res:
                for picking in order.picking_ids:
                    if not picking.client_po:
                        picking.client_po = order.client_po
        return True

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['client_po'] = self.client_po
        res['rfq_num'] = self.rfq_num
        return res
