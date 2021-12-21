from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ship_type = fields.Selection(related='carrier_id.ship_type', string='Ship Type')