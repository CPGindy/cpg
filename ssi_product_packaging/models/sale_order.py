from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    product_packaging_id = fields.Many2one('product.packaging',string='Product Packaging')