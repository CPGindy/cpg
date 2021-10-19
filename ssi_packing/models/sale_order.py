from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_number = fields.Char(string="Vendor Number", help="Order/Partner/Vendor Number")