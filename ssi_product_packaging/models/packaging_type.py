from odoo import models, fields, api


class PackagingType(models.Model):
    _name = 'packaging.type'
    
    name = fields.Char(string='Name')