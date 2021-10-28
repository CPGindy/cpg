# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'


    license_item = fields.One2many('license.item', 'product_id', string='Licensed Items')
    license_product = fields.One2many('license.product', 'product_id', string='Licensed Product')
