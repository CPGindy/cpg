# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.tools import float_is_zero


class RoyaltyPool(models.Model):
    _name = 'ssi_royalty.pool'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Royalty Pool'
    
    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    artist_id = fields.Many2one('res.partner', string='Artist')
    licensor_id = fields.Many2one('res.partner', string='Licensor')
    balance = fields.Float(string='Current Balance', readonly=1)
    pool_line = fields.One2many('ssi_royalty.pool.line', 'pool_id', string='Pool Line')  
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('royalty.pool.sequence') or _('New')
        return super(RoyaltyPool, self).create(vals)
    
    
    
class RoyaltyPoolLine(models.Model):
    _name = 'ssi_royalty.pool.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Royalty Pool Line'
    
    date = fields.Date(string='Date')
    royalty_id = fields.Many2one('ssi_royalty.ssi_royalty', string='Royalty')
    memo = fields.Char(string='Memo')
    value_type = fields.Selection([('in', 'In'),('out', 'Out')], string='Value Type')
    value = fields.Float(string='Value')
    pool_value = fields.Float(string='Pool')
    pool_id = fields.Many2one('ssi_royalty.pool', string='Royalty Pool')
