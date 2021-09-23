from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LicenseProduct(models.Model):
    _name = 'license.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product_id'
    _description = "License Product"
    
    royalty_rate = fields.Float(string='Royalty Rate')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    license_item_id = fields.Many2one('license.item', string='Art')
    artist_id = fields.Many2one('res.partner', related="license_item_id.license_id.artist_id")
