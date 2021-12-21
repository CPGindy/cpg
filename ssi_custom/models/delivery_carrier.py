from odoo import models, fields, api


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    ship_type = fields.Selection([('1', 'Pickup Common (1)'),('2', 'Truck (2)'),('3', 'Rail (3)'),('4', 'Cartage (4)'),('5', 'LTL Truck - common (5)'),
    ('6', 'PKG - common (6)'),('7', 'Piggy back (7)'),('8', 'Water (8)')], string='Ship Type')