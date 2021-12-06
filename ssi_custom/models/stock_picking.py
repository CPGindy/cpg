from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ship_type = fields.Selection([('1', 'Pickup Common'),('2', 'Truck'),('3', 'Rail'),('4', 'Cartage'),('5', 'LTL Truck - common'),
    ('6', 'PKG - common'),('7', 'Piggy back'),('8', 'Water')], string='Ship Type')