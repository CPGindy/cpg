from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    product_packaging_id = fields.Many2one('product.packaging',string='Product Packaging')