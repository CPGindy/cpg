from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sku_lookup_line = fields.One2many('sku.lookup', 'product_id', string="Customer SKU's Lookup")