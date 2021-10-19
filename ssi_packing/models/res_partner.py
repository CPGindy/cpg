from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    store_number = fields.Char(string="Store Number", string="Partner/Store Number")