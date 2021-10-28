from odoo import models, fields, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    
    product_packaging_id = fields.Many2one('product.packaging',string='Product Packaging')