from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LicenseItem(models.Model):
    _name = 'license.item'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    _rec_name = 'art_license_number'
    _description = "License Item"
    
    
    license_product_id = fields.Many2one('license.product', string='Licensed Product')
    end_date = fields.Date(string='End Date')
#     art_license_number = fields.Char(string='Art License Number', required=True, copy=False, index=True)
    art_license_number = fields.Char(string='Art License Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    reference_image = fields.Binary(string='Reference Image')
    is_active = fields.Boolean(string='Is Active')
    territory = fields.Selection([('north_america', 'North America'),('worldwide', 'World Wide')], string='Territory')
    sell_off_date = fields.Date(string='Sale Off Date')
    note = fields.Html(string='Notes')
    licensed_for = fields.Many2many('license.category', string='Licensed For')
    license_id = fields.Many2one('license.license', string='License')
    license_product_line = fields.One2many('license.product', 'license_item_id', string='Licensed Product Line')
    product_id = fields.Many2one('product.product', string='Product')
    item_pool_id = fields.One2many('license.item.pool', 'license_item_id', string='License Item Pool')
    description = fields.Text(string='Description')
    royalty_count = fields.Integer(string='Royalty', compute='_get_royalty_count')
    reference_image_interior = fields.Binary(string='Reference Image Interior')
    reference_image_front = fields.Binary(string="Refernce Image Front")
    
    
    def _get_royalty_count(self):
        for record in self:
            royalty_count = self.env['ssi_royalty.ssi_royalty'].sudo().search_count([('licensed_item', '=', record.id)])
            record.royalty_count = royalty_count

            
    def action_view_royalty(self):
        royalty_lines = self.env['ssi_royalty.ssi_royalty'].search([('licensed_item', '=', self.id)])
        royalty_ids = []
        for line in royalty_lines:
            royalty_ids.append(line.id)    
        return {  
             'name': _('Royalty'),
            'view_mode': 'tree', 			
            'view_id': self.env.ref('ssi_royalty.ssi_royalty_view_list').id, 			
            'view_type': 'form', 
            'res_model': 'ssi_royalty.ssi_royalty', 			
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', royalty_ids)],
            'target': 'current',
        }
    
#     @api.model
#     def create(self, vals):
#         if vals.get('art_license_number', _('New')) == _('New'):
#             vals['art_license_number'] = self.env['ir.sequence'].next_by_code('license.item.sequence') or _('New')
#         return super(LicenseItem, self).create(vals)
    
    def create_royalty(self):
        view_id = self.env.ref('ssi_royalty.ssi_royalty_view_form')
        context = self._context.copy()
        return {  
             'name': _('Royalty'),
            'view_mode': 'form', 			
            'view_id': view_id.id, 			
            'view_type': 'form', 
            'context': {
                'default_licensed_item': self.id,
                'default_license_id': self.license_id.id,
                'default_artist_id': self.license_id.artist_id.id,
                'default_licensor_id': self.license_id.licensor_id.id,
                'default_date': date.today(),
                'default_source_document': self.art_license_number,
                'default_license_product_id': self.license_product_line[0].id,
                'default_royalty_rate': self.license_product_line[0].royalty_rate,
                        },
            'res_model': 'ssi_royalty.ssi_royalty', 			
            'type': 'ir.actions.act_window', 			
            'target': 'new',
        }
    
    
class LicenseItemPool(models.Model):
    _name = 'license.item.pool'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'License Item Pool'
    _rec_name = 'name'

    
    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    license_item_id = fields.Many2one('license.item', string='License Item')
    paid_date = fields.Date(string='Paid Date')
    first_sale_date = fields.Date(string='First Sale')
    value = fields.Float(string='Value')
    status = fields.Selection([('draft', 'Draft'),('paid', 'Paid')],default='draft', string='Status')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('license.item.pool.sequence') or _('New')
        return super(LicenseItemPool, self).create(vals)
    
    
    def pay_pool(self):
        for rec in self:
            rec.write({'status': 'paid'})
    
    
class LicensedCategory(models.Model):
    _name = 'license.category'
    
    
    name = fields.Char(String='Name')
    