from odoo import api, models, fields


class PurchaseOrderLines(models.Model):
    _inherit = 'purchase.order.line'

    product_part = fields.Char(
        string="Part", related="product_id.product_part")
    product_mfr = fields.Char(string="MFR", related="product_id.product_mfr")
    product_mfr_name = fields.Char(
        string="MFR Name", related="product_id.product_mfr_name")
    product_material_code = fields.Char(
        string="Material Code", related="product_id.product_material_code")
    product_smacc_code = fields.Char(
        string="SMACC Code", related="product_id.product_smacc_code")
    product_samj_code = fields.Char(
        string="SAMJ Code", related="product_id.product_samj_code")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.multi
    def _set_default_picking_type(self):
        return self.env['stock.picking.type']

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Deliver To',
        states=READONLY_STATES, required=True,
        default=_set_default_picking_type,
        help="This will determine operation type of incoming shipment")
