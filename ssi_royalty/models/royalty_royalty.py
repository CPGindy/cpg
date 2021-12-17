from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
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
            vals['name'] = self.env['ir.sequence'].next_by_code('royalty.royalty.sequence') or _('New')
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
        for rec in self.filtered(lambda a: not a.is_report_approved):
            if rec.licensor_id:
                royalty_line = [(6, 0, [rec.id])]
                search_report = self.env['ssi_royalty.report'].search([('licensor_id', '=', rec.licensor_id.id), ('status', '=', 'draft')], limit=1)
                if search_report and search_report.status not in ['posted', 'paid']:
                    search_report.update({'royalty_line_id' : [(4, rec.id)]})
                else:
                    header_vals = {
                        'status': 'draft',
                        'licensor_id': rec.licensor_id.id,
                        'report_date': date.today(),
                        'royalty_line_id' : royalty_line
                    }
                    search_report = self.env['ssi_royalty.report'].create(header_vals)
                for royalty_line in search_report.royalty_line_id.filtered(lambda l: l.type == "sale_on_item"):
                    pool_id = self.env['ssi_royalty.pool'].search([('artist_id', '=', royalty_line.artist_id.id)])
                    pool_lines = self.env['ssi_royalty.pool.line'].search([('pool_id', '=', pool_id.id), ('value_type', '=', 'in'), ('first_sale_date', '=', False), ('art_id', '=', royalty_line.licensed_item.id)])
                    for pool_line in pool_lines:
                        pool_line.write({'first_sale_date': datetime.now()})
            else:
                raise UserError(_('Please Select Licensor Before Generating Report'))
            rec.payment_status = 'reported'

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
    artist_id = fields.Many2one('res.partner', string='Artist')
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

    @api.depends('report_date')
    def _compute_dates(self):
        for rec in self:
            rec.date_year = rec.report_date.year
            rec.date_month = rec.report_date.month
            # self.date_year = int(datetime.strptime(self.report_date, '%Y-%m-%d %H:%M:%S').year)
            # self.date_month = int(datetime.strptime(self.report_date, '%Y-%m-%d %H:%M:%S').month)

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
        # search_pool = self.env['ssi_royalty.pool'].search([('artist_id', '=', self.artist_id.id)])
        # if search_pool:
        #     available_balance = search_pool.balance
        #     return {
        #     'name': _("Make a Payment"),
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'pool.payment',
        #     'view_id': self.env.ref('ssi_royalty.wizard_pool_payment_form').id,
        #     'target': 'new',
        #     'context': {
        #         'default_artist_id': self.artist_id.id,
        #         'default_licensor_id': self.licensor_id.id,
        #         'default_available_balance': available_balance,
        #         'default_balance_to_pay': self.remaining_balance,
        #         'default_advance_payment': self.advanced_payment,
        #         'default_memo': self.name,
        #         'default_pool_report_id': self.id,
        #         'default_vendor_journal_id': self.vendor_journal_id.id,
        #     }}
        # return {
        #     'name': _("Make a Payment"),
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'pool.payment',
        #     'view_id': self.env.ref('ssi_royalty.wizard_pool_payment_form').id,
        #     'target': 'new',
        #     'context': {
        #         'default_artist_id': self.artist_id.id,
        #         'default_licensor_id': self.licensor_id.id,
        #         'default_available_balance': 0.0,
        #         'default_balance_to_pay': self.remaining_balance,
        #         'default_advance_payment': self.advanced_payment,
        #         'default_memo': self.name,
        #         'default_pool_report_id': self.id,
        #         'default_vendor_journal_id': self.vendor_journal_id.id,
        #     }}
