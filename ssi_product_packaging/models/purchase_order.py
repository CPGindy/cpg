from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    
    product_packaging_id = fields.Many2one('product.packaging',string='Product Packaging')
    
    
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    
    product_packaging_id = fields.Many2one('product.packaging',string='Product Packaging')