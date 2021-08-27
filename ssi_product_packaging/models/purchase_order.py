from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    
    product_packaging_id = fields.Many2one('product.packaging',string='Product Packaging')