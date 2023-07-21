from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
from odoo.tools import float_is_zero
import time
import math


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
    type = fields.Selection([('advance', 'Advance'),('sale_on_item', 'Sale on Item'),('flat_fee', 'Flat Fee'),('not_licensed', 'Not Licensed')], string='Type')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    licensed_item = fields.Many2one('license.item', string='Licensed Item')
    description = fields.Char(string='Description', related='licensed_item.description')
    license_product_id = fields.Many2one('license.product', string='Licensed Product')
    invoice_product_id = fields.Many2one('product.product', string='Invoice Product')
    license_id = fields.Many2one('license.license', string='License')
    artist_id = fields.Many2one('res.partner', string='Artist')
    item_value = fields.Float(string='Item Value')
    licensor_id = fields.Many2one('res.partner', string='Licensor', related='license_id.licensor_id', store=True)
    date = fields.Date(string='Date')
    source_document = fields.Char(string='Source Document')
    payment_status = fields.Selection([('rejected', 'Rejected'),('draft', 'New'),('reported', 'Reported')],
                                      string='Payment Status', track_visibility="onchange", readonly=True, default='draft')
    royalty_rate = fields.Float(string='Royalty Rate')
    royalty_value = fields.Float(string='Royalty Value')
    royalty_report_id = fields.Many2one('ssi_royalty.report', string='Royalty Report')
    report_status = fields.Selection(related='royalty_report_id.status')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    currency_id = fields.Many2one('res.currency', string='Currency')
    account_id = fields.Many2one('account.account', store=True, readonly=False, string='Account',
        default=_default_account_id, domain="[('company_id', '=', company_id)]", help="A royalty account is expected")
    is_report_approved = fields.Boolean(string='Is Report Approved')


    @api.onchange('type')
    def _onchange_type(self):
        for rec in self:
            if rec.type == 'sale_on_item':
                for royalty_line in rec.filtered(lambda l: l.type == "sale_on_item"):
                    pool_id = self.env['ssi_royalty.pool'].search([('artist_id', '=', royalty_line.artist_id.id)])
                    pool_lines = self.env['ssi_royalty.pool.line'].search([('pool_id', '=', pool_id.id), ('value_type', '=', 'in'), ('first_sale_date', '=', False), ('art_id', '=', royalty_line.licensed_item.id)])
                    for pool_line in pool_lines:
                        pool_line.write({'first_sale_date': datetime.now()})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            format_name = 'ROL/'+time.strftime("%m", time.localtime()) + time.strftime("%y", time.localtime())+'/'+self.env['ir.sequence'].next_by_code('royalty.royalty.sequence')
            vals['name'] = format_name or _('New')
        res = super(Royalty, self).create(vals)
        for royalty_line in res.filtered(lambda l: l.type == "sale_on_item"):
            pool_id = self.env['ssi_royalty.pool'].search([('artist_id', '=', royalty_line.artist_id.id)])
            pool_lines = self.env['ssi_royalty.pool.line'].search([('pool_id', '=', pool_id.id), ('value_type', '=', 'in'), ('first_sale_date', '=', False), ('art_id', '=', royalty_line.licensed_item.id)])
            for pool_line in pool_lines:
                pool_line.write({'first_sale_date': datetime.now()})
        return res

    def unlink_from_report(self):
        for rec in self:
            if rec.royalty_report_id:
                rec.update({'royalty_report_id': None})

    def action_generate_report(self):
        confirm_report = self.env['royalty.report.confirm'].create({'royalty_ids': self.ids})
        return {
             'name': _('Confirm Report Date'),
            'view_mode': 'form',
            'view_id': self.env.ref('ssi_royalty.royalty_report_confirm_views').id,
            'view_type': 'form',
            'res_model': 'royalty.report.confirm',
            'type': 'ir.actions.act_window',
            'res_id': confirm_report.id,
            'target': 'new',
        }


    def action_reject(self):
        for rec in self.filtered(lambda r: not r.royalty_report_id or r.royalty_report_id.status == 'draft'):
            rec.payment_status = 'rejected'
            rec.royalty_report_id = False
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Royalty has been rejected.'),
                'type': 'success',
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            },
        }

    def action_draft(self):
        for rec in self.filtered(lambda r: r.payment_status == 'rejected'):
            rec.payment_status = 'draft'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Royalty has been reset to draft.'),
                'type': 'success',
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            },
        }


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
    licensor_id = fields.Many2one('res.partner', string='Licensor')
    memo = fields.Char(string='Memo')
    total_due = fields.Float(string='Total Due', compute='_compute_total_due')
    royalty_line_id = fields.One2many('ssi_royalty.ssi_royalty', 'royalty_report_id', string='Royalty Lines', ondelete='restrict')
    status = fields.Selection([('draft', 'Draft'),('posted', 'Posted'),('paid', 'Paid')], string='Status')
    report_date = fields.Date(string='Initial Report Date')
    currency_id = fields.Many2one('res.currency', string='Currency')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    vendor_journal_id = fields.Many2one('account.journal', string='Journal', check_company=True, domain="[('type', 'in', 'purchase', ('company_id', '=', company_id)]",
        default=_default_vendor_journal_id, help="The payment method used when the expense is paid by the Vendor.")
    move_id = fields.Many2one('account.move', string='Vendor Bill', readonly=1, track_visibility="onchange")
    paid_by_pool = fields.Float(string='Balance Paid By Pool')
    advanced_payment = fields.Float(string='Advanced Payment', compute='_compute_advanced_paid')
#     remaining_balance = fields.Float(string='Remaining Balance', compute='_compute_remaining_balance')
    paid_by_vendor_bill = fields.Float(string='Paid By Vendor Bill')
    date_year = fields.Integer(string='Year of the Date (used in reporting)', compute="_compute_dates", store=True)
    date_month = fields.Integer(string="Month of the Date (used in reporting)", compute="_compute_dates", store=True)
    rejected = fields.Boolean(string='Rejected', default=False, tracking=True)
    report_name = fields.Char(string="Report Name", compute="_compute_report_name")
    net_royalty_paid = fields.Float(string="Net Royalty Total", compute="_compute_net_royalty_paid")


    def _compute_net_royalty_paid(self):
        for rec in self:
            amount = 0.0
            if rec.royalty_line_id and rec.royalty_line_id.filtered(lambda x: x.artist_id):
                artists = list(set([line.artist_id for line in rec.royalty_line_id.filtered(lambda x: x.artist_id)]))
                for artist in artists:
                    search_pool= self.env['ssi_royalty.pool'].search([('artist_id', '=', artist.id)], limit=1)
                    if search_pool:
                        pool_lines = self.env['ssi_royalty.pool.line'].search([('value_type', '=', 'out'),('pool_id', '=', search_pool.id),('reference', '=', rec.id)])
                        if pool_lines:
                            for p_line in pool_lines:
                                amount += p_line.pool_value
            
            rec.net_royalty_paid = rec.total_due - amount


    @api.depends('report_date')
    def _compute_dates(self):
        for rec in self:
            rec.date_year = rec.report_date.year
            rec.date_month = rec.report_date.month
            # self.date_year = int(datetime.strptime(self.report_date, '%Y-%m-%d %H:%M:%S').year)
            # self.date_month = int(datetime.strptime(self.report_date, '%Y-%m-%d %H:%M:%S').month)

    @api.depends('name', 'report_date')
    def _compute_report_name(self):
        for rec in self:
            name = rec.name
            if rec.report_date:
                month = rec.report_date.month
                quarter_dictionary = {
                    "Q1" : [1,2,3],
                    "Q2" : [4,5,6],
                    "Q3" : [7,8,9],
                    "Q4" : [10,11,12]
                }
                for key,values in quarter_dictionary.items():
                    for value in values:
                        if value == month:
                            name = name + " ("+ str(key) + " - " + str(rec.report_date.year) +")"
            rec.report_name = name




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

#     @api.depends('paid_by_pool','total_due')
#     def _compute_remaining_balance(self):
#         for rec in self:
#             rec.remaining_balance = rec.total_due - rec.paid_by_pool - rec.paid_by_vendor_bill

#     @api.onchange('total_due')
#     def _onchange_total(self):
#         for rec in self:
#             if rec.total_due:
#                 rec.remaining_balance = rec.total_due

    def reject_royalty(self):
        for rec in self:
            if rec.status != 'draft':
                raise UserError(_("You can only reject draft report"))
            rec.update({'rejected': True})
    
    def restore_royalty(self):
        for rec in self:
            rec.update({'rejected': False})
            
    def send_royalty_report(self):
        
        self.ensure_one()
        lang = self.env.context.get('lang')
        mail_template = self.env.ref('ssi_royalty.royalty_report_quarter_email_template')

        ctx = {
            'default_model': 'ssi_royalty.report',
            'default_res_id': self.ids[0],
            'default_use_template': bool(mail_template),
            'default_template_id': mail_template.id if mail_template else None,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('royalty.report.sequence') or _('New')
        res = super(RoyaltyReport, self).create(vals)
        return res

    def unlink(self):
        for rec in self.filtered(lambda a: a.status != 'draft'):
            if rec.royalty_line_id:
                for royalty in rec.royalty_line_id:
                    royalty.update({'is_report_approved': False})

        return super(RoyaltyReport, self).unlink()

    def open_vendor_bill(self):
        try:
            form_view_id = self.env.ref("account.view_move_form").id
        except Exception as e:
            form_view_id = False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.move_id.id,
            'views': [(form_view_id, 'form')],
            'target': 'current',
        }

    def post_journal_staus(self):
        self.write({'status': 'posted'})

    def make_payment_pool(self):
        if self.rejected:
            raise UserError(_("You can't make bill for rejected report"))
        payment = self.env['pool.payment'].create({
            'licensor_id': self.licensor_id.id,
            'memo': self.name,
            'pool_report_id': self.id,
            'vendor_journal_id': self.vendor_journal_id.id,
        })
        artists = {}
        for line in self.royalty_line_id:
            pool = self.env['ssi_royalty.pool'].search([('artist_id', '=', line.artist_id.id)], limit=1)
            available_balance = pool.balance if pool else 0
            advance = line.royalty_value if line.type == 'advance' else 0
            vals = {
                'pool_payment_id': payment.id,
                'artist_id': line.artist_id.id,
                'balance_to_pay': line.royalty_value,
                'available_balance': available_balance,
                'advance_payment': advance,
                'license_item_id': line.licensed_item.id,
            }
            if line.artist_id.id in artists.keys():
                payment_line = artists[line.artist_id.id]
                payment_line.balance_to_pay += vals['balance_to_pay']
                payment_line.advance_payment += vals['advance_payment']
            else:
                payment_line = self.env['pool.payment.line'].create(vals)
                artists.update({line.licensed_item.id: payment_line})
        payment.write({
            'balance_to_pay': sum([max([line.balance_to_pay - line.available_balance, 0]) for line in payment.pool_payment_line_ids])
        })

        return {
            'name': _("Make a Payment"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pool.payment',
            'res_id': payment.id,
            'view_id': self.env.ref('ssi_royalty.wizard_pool_payment_form').id,
            'target': 'new',
        }
    

    def action_make_payment_pool(self):
        all_payments = []
        for rec in self.filtered(lambda x: x.status == 'draft'):
            payment = self.env['pool.payment'].create({
                'licensor_id': rec.licensor_id.id,
                'memo': rec.name,
                'pool_report_id': rec.id,
                'vendor_journal_id': rec.vendor_journal_id.id,
            })
            artists = {}
            for line in rec.royalty_line_id:
                pool = self.env['ssi_royalty.pool'].search([('artist_id', '=', line.artist_id.id)], limit=1)
                available_balance = pool.balance if pool else 0
                advance = line.royalty_value if line.type == 'advance' else 0
                vals = {
                    'pool_payment_id': payment.id,
                    'artist_id': line.artist_id.id,
                    'balance_to_pay': line.royalty_value,
                    'available_balance': available_balance,
                    'advance_payment': advance,
                    'license_item_id': line.licensed_item.id,
                }
                if line.artist_id.id in artists.keys():
                    payment_line = artists[line.artist_id.id]
                    payment_line.balance_to_pay += vals['balance_to_pay']
                    payment_line.advance_payment += vals['advance_payment']
                else:
                    payment_line = self.env['pool.payment.line'].create(vals)
                    artists.update({line.licensed_item.id: payment_line})
            payment.write({
                'balance_to_pay': sum([max([line.balance_to_pay - line.available_balance, 0]) for line in payment.pool_payment_line_ids])
            })
            all_payments.append(payment)
        if all_payments:
            for a_payment in all_payments:
                a_payment._compute_balance_to_be_posted()
                a_payment.action_make_payment()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Payment Was Successfully Made'),
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
            },
        }
