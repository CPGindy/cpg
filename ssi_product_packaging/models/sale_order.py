import io
import base64
import logging
from odoo.exceptions import UserError

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    product_packaging_id = fields.Many2one('product.packaging',string='Product Packaging')
        
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    product_packaging_id = fields.Many2one('product.packaging',string='Product Packaging')
    
