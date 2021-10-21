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
    balance = fields.Float(string='Current Balance', readonly=1, compute="_compute_balance")
    pool_line = fields.One2many('ssi_royalty.pool.line', 'pool_id', string='Pool Line')

    @api.depends('pool_line')
    def _compute_balance(self):
        for rec in self:
            balance = 0
            for line in rec.pool_line:
                if line.value_type == 'in' and line.is_active:
                    balance += line.pool_value
                elif line.value_type == 'out':
                    balance -= line.pool_value
            rec.balance = balance

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
    art_id = fields.Many2one('license.item', string="Artwork")
    first_sale_date = fields.Datetime(string="First Sale Date", readonly=True)
    is_active = fields.Boolean(string="Is Active", default=False, compute="_compute_active", readonly=True)

    @api.depends('first_sale_date')
    def _compute_active(self):
        for rec in self:
            if rec.first_sale_date:
                rec.is_active = True
            else:
                rec.is_active = False
