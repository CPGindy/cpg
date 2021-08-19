# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.tools import float_is_zero


class Royalty(models.Model):
    _name = 'ssi_royalty.ssi_royalty'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "Royalty"
    
    
    @api.model
    def _default_vendor_journal_id(self):
        default_company_id = self.default_get(['company_id'])['company_id']
        return self.env['account.journal'].search([('type', 'in', ['purchase']), ('company_id', '=', default_company_id)], limit=1)

    @api.model
    def _default_account_id(self):
        return self.env['ir.property']._get('property_account_expense_categ_id', 'product.category')
    
    name = fields.Char(string='Contract', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    type = fields.Selection([('advance', 'Advance'),('sale_on_item', 'Sale on Item'),('flat_fee', 'Flat Fee')], string='Type')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    licensed_item = fields.Many2one('license.item', string='Licensed Item')
    license_product_id = fields.Many2one('license.product', string='Licensed Product')
    license_id = fields.Many2one('license.license', string='License')
    artist_id = fields.Many2one('res.partner', string='Artist')
    item_value = fields.Float(string='Item Value')
    licensor_id = fields.Many2one('res.partner', string='Licensor', related='license_id.licensor_id')
    date = fields.Date(string='Date')
    source_document = fields.Char(string='Source Document')
    payment_status = fields.Selection([('draft', 'Draft'),('posted', 'Posted'),('paid', 'Paid')], string='Payment Status',track_visibility="onchange")
    royalty_rate = fields.Float(string='Royalty Rate')
    royalty_value = fields.Float(string='Royalty Value')
    royalty_report_id = fields.Many2one('ssi_royalty.report', string='Royalty Report')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    currency_id = fields.Many2one('res.currency', string='Currency')
    account_id = fields.Many2one('account.account', store=True, readonly=False, string='Account',
        default=_default_account_id, domain="[('company_id', '=', company_id)]", help="A royalty account is expected")
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('royalty.royalty.sequence') or _('New')
        return super(Royalty, self).create(vals)
 

    def action_generate_report(self):
        for rec in self:
            if rec.artist_id:
                royalty_line = [(6, 0, [rec.id])]
                search_report = self.env['ssi_royalty.report'].search([('artist_id', '=', rec.artist_id.id)], limit=1)
                if search_report and search_report.status not in ['posted', 'paid']:
                    search_report.update({'royalty_line_id' : [(4, rec.id)]})
                else:
                    header_vals = {
                        'artist_id': rec.artist_id.id,
                        'status': 'draft',
                        'licensor_id': rec.licensor_id.id,
                        'report_date': date.today(),
                        'royalty_line_id' : royalty_line
                    }
                    self.env['ssi_royalty.report'].create(header_vals)
            else:
                raise UserError(_('Please Select Artist Before Generating Report'))
                
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Royalty Report Has Been Successfully Created.'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
        return notification
    
    
    
class RoyaltyReport(models.Model):
    _name = 'ssi_royalty.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "Royalty Report"
    
    @api.model
    def _default_vendor_journal_id(self):
        default_company_id = self.default_get(['company_id'])['company_id']
        return self.env['account.journal'].search([('type', 'in', ['purchase']), ('company_id', '=', default_company_id)], limit=1)

    name = fields.Char(string='Contract', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    artist_id = fields.Many2one('res.partner', string='Artist')
    licensor_id = fields.Many2one('res.partner', string='Licensor')
    memo = fields.Char(string='Memo')
    total_due = fields.Float(string='Total Due', compute='_compute_total_due')
    royalty_line_id = fields.One2many('ssi_royalty.ssi_royalty', 'royalty_report_id', string='Royalty Lines')
    status = fields.Selection([('draft', 'Draft'),('posted', 'Posted'),('paid', 'Paid')], string='Status')
    report_date = fields.Date(string='Initial Report Date')
    currency_id = fields.Many2one('res.currency', string='Currency')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    vendor_journal_id = fields.Many2one('account.journal', string='Journal', check_company=True, domain="[('type', 'in', 'purchase', ('company_id', '=', company_id)]",
        default=_default_vendor_journal_id, help="The payment method used when the expense is paid by the Vendor.")
    move_id = fields.Many2one('account.move', string='Vendor Bill', readonly=1, track_visibility="onchange")
    paid_by_pool = fields.Float(string='Balance Paid By Pool')
    advanced_payment = fields.Float(string='Advanced Payment', compute='_compute_advanced_paid')
    remaining_balance = fields.Float(string='Remaining Balance', compute='_compute_remaining_balance')
    paid_by_vendor_bill = fields.Float(string='Paid By Vendor Bill')


    
    @api.depends('royalty_line_id')
    def _compute_total_due(self):
        for rec in self:
            total = 0
            if rec.royalty_line_id:
                for line in rec.royalty_line_id:
                    total += line.royalty_value
                rec.total_due = total
            else:
                rec.total_due = 0
                
    @api.depends('royalty_line_id')
    def _compute_advanced_paid(self):
        for rec in self:
            total = 0
            if rec.royalty_line_id.filtered(lambda r: r.type == 'advance'):
                for line in rec.royalty_line_id.filtered(lambda r: r.type == 'advance'):
                    total += line.royalty_value
                rec.advanced_payment = total
            else:
                rec.advanced_payment = 0
                
    @api.depends('paid_by_pool','total_due')
    def _compute_remaining_balance(self):
        for rec in self:
            rec.remaining_balance = rec.total_due - rec.paid_by_pool - rec.paid_by_vendor_bill
                
    @api.onchange('total_due')
    def _onchange_total(self):
        for rec in self:
            if rec.total_due:
                rec.remaining_balance = rec.total_due
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('royalty.report.sequence') or _('New')
        return super(RoyaltyReport, self).create(vals)
    
    
    def post_journal_staus(self):
        self.write({'status': 'posted'})

                                
    def make_payment_pool(self):
        search_pool = self.env['ssi_royalty.pool'].search([('licensor_id', '=', self.licensor_id.id)])
        if search_pool:
            available_balance = search_pool.balance
            return {
            'name': _("Make a Payment"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pool.payment',
            'view_id': self.env.ref('ssi_royalty.wizard_pool_payment_form').id,
            'target': 'new',
            'context': {
                'default_licensor_id': self.licensor_id.id,
                'default_available_balance': available_balance,
                'default_balance_to_pay': self.remaining_balance,
                'default_advance_payment': self.advanced_payment,
                'default_memo': self.name,
                'default_pool_report_id': self.id,
                'default_vendor_journal_id': self.vendor_journal_id.id,
            }}
        else:
            raise UserError(_('No Pool Payment Record Found For This Licensor'))
    

