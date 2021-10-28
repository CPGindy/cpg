from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LicenseLicense(models.Model):
    _name = 'license.license'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'contract_id'
    _description = "License"
    
    
    type = fields.Selection([('type1', 'Type 1'),('type2', 'Type 2'),('type3', 'Type 3')], string='Type')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    contract_id = fields.Char(string='Contract', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    artist_id = fields.Many2one('res.partner', string='Artist')
    licensor_id = fields.Many2one('res.partner', string='Licensor')
    license_product_id = fields.Many2one('license.product', string='Licensed Product')
    license_item = fields.One2many('license.item', 'license_id', string='Licensed Items')
    
    
    @api.model
    def create(self, vals):
        if vals.get('contract_id', _('New')) == _('New'):
            vals['contract_id'] = self.env['ir.sequence'].next_by_code('license.license.sequence') or _('New')
        return super(LicenseLicense, self).create(vals)