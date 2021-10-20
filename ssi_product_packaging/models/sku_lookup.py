from odoo import models, fields, api


class CustomerSkuLookup(models.Model):
    _name = 'sku.lookup'
    _description = 'Customer SKU Lookup'
    
    product_id = fields.Many2one('product.product', string='Product')
    customer_sku = fields.Char(string="Customer SKU")
    partner_id = fields.Many2one('res.partner', string="Customer")