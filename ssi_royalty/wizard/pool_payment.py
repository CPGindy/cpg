from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime


class PoolPaymentLine(models.TransientModel):
    _name = 'pool.payment.line'

    artist_id = fields.Many2one('res.partner', string='Artist', readonly=True)
    available_balance = fields.Float(string='Available Pool Balance', readonly=True)
    balance_to_pay = fields.Float(string="Balance To Pay", readonly=True)
    advance_payment = fields.Float(string='Advance Payment', readonly=True)
    pool_payment_id = fields.Many2one('pool.payment', string="Payment Record")
    sale_balance = fields.Float(string="Sale Balance", compute="_compute_sale_balance")
    pool_covered = fields.Float(string="Covered by Pool", compute="_compute_pool_covered")
    remaining_balance = fields.Float(string="Remaining Balance", compute="_compute_remaining_balance")
    license_item_id = fields.Many2one('license.item', string="Art", readonly=True)

    @api.depends('balance_to_pay', 'advance_payment')
    def _compute_sale_balance(self):
        for rec in self:
            rec.sale_balance = rec.balance_to_pay - rec.advance_payment

    @api.depends('sale_balance', 'available_balance')
    def _compute_pool_covered(self):
        for rec in self:
            rec.pool_covered = rec.sale_balance if rec.available_balance >= rec.sale_balance else rec.available_balance

    @api.depends('pool_covered', 'balance_to_pay')
    def _compute_remaining_balance(self):
        for rec in self:
            rec.remaining_balance = rec.balance_to_pay - rec.pool_covered


class PoolPayment(models.TransientModel):
    _name = "pool.payment"

    artist_id = fields.Many2one('res.partner', string='Artist', readonly=True)
    licensor_id = fields.Many2one('res.partner', string='Licensor', readonly=True)
    available_balance = fields.Float(string='Available Pool Balance', readonly=True)
    balance_to_pay = fields.Float(string="Balance To Pay", readonly=True)
    memo = fields.Char(string='Memo')
    pool_report_id = fields.Many2one('ssi_royalty.report', string='Report')
    advance_payment = fields.Float(string='Advance Payment', readonly=True)
    journal_balance = fields.Float(string='Balance To Be Posted On Journal', compute='_compute_balance_to_be_posted')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    vendor_journal_id = fields.Many2one('account.journal', string='Journal')
    move_id = fields.Many2one('account.move', string='Vendor Bill', readonly=True)
    pool_payment_line_ids = fields.One2many('pool.payment.line', 'pool_payment_id', string="Payment Lines")

    @api.depends('available_balance', 'balance_to_pay')
    def _compute_balance_to_be_posted(self):
        total_remaining = 0
        for artist in set(self.pool_payment_line_ids.mapped('artist_id')):
            lines = self.pool_payment_line_ids.filtered(lambda line: line.artist_id == artist)
            pool = self.env['ssi_royalty.pool'].search([('artist_id', '=', artist.id)], limit=1)
            if not pool:
                pool_vals = {
                    'artist_id': artist.id,
                    'licensor_id': self.licensor_id.id,
                    'balance': 0.0,
                }
                pool = self.env['ssi_royalty.pool'].create(pool_vals)
            no_advance = sum(lines.filtered(lambda line: not line.advance_payment).mapped('balance_to_pay'))
            advance = sum(lines.filtered(lambda line: line.advance_payment).mapped('advance_payment'))
            pool_balance = pool.balance + advance
            pool_diff = no_advance - pool_balance
            if pool_diff <= 0:
                remaining_balance = 0
            else:
                remaining_balance = pool_balance - no_advance
            total_remaining += remaining_balance
            total_remaining += advance
        self.journal_balance = total_remaining


    def make_payment(self):
        # create the vendor bill
        journal = self.vendor_journal_id
        account_date = date.today()
        payment_terms = self.licensor_id.property_supplier_payment_term_id
        move_values = {
            'journal_id': journal.id,
            'company_id': self.company_id.id,
            'partner_id': self.licensor_id.id,
            'move_type': 'in_invoice',
            'invoice_date': account_date,
            'ref': self.pool_report_id.name,
            'name': '/',
            'invoice_payment_term_id': payment_terms.id,
        }
        move_rec = self.env['account.move'].create(move_values)
        self.move_id = move_rec.id
        pro_id = self.env['ir.config_parameter'].sudo().get_param('royalty_product_item')
        product = self.env['product.product'].search([('id', '=', pro_id)])

        paid_by_pool = 0
        for artist in set(self.pool_payment_line_ids.mapped('artist_id')):
            lines = self.pool_payment_line_ids.filtered(lambda line: line.artist_id == artist)
            pool = self.env['ssi_royalty.pool'].search([('artist_id', '=', artist.id)], limit=1)
            if not pool:
                pool_vals = {
                    'artist_id': artist.id,
                    'licensor_id': self.licensor_id.id,
                    'balance': 0.0,
                }
                pool = self.env['ssi_royalty.pool'].create(pool_vals)
            advance = sum(lines.mapped('advance_payment'))
            balance = sum(lines.mapped('balance_to_pay')) - advance

            # add advance to pool
            if advance > 0:
                for advance_line in lines.filtered(lambda l: l.advance_payment > 0):
                    line_vals = {
                        'date': date.today(),
                        'memo': self.memo + " On Advance Payment",
                        'reference': self.pool_report_id.id,
                        'value_type': 'in',
                        'pool_value': advance_line.advance_payment,
                        'value': pool.balance + advance_line.advance_payment,
                        'pool_id': pool.id,
                        'art_id': advance_line.license_item_id.id,
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    # pool.update({'balance': line_vals['value']})

            for sale_line in lines.filtered(lambda l: not l.advance_payment > 0):
                if sale_line.license_item_id and sale_line.artist_id and sale_line.create_date:
                    pool_id = self.env['ssi_royalty.pool'].search([('artist_id', '=', sale_line.artist_id.id)])
                    pool_lines = self.env['ssi_royalty.pool.line'].search([('pool_id', '=', pool_id.id), ('value_type', '=', 'in'), ('first_sale_date', '=', False), ('art_id', '=', sale_line.license_item_id.id), ('create_date', '<=', sale_line.create_date)])
                    for pool_line in pool_lines:
                        pool_line.write({'first_sale_date': datetime.now()})

            # subtract total without advance from the pool
            pool_diff = balance - pool.balance
            if pool_diff <= 0:
                remaining_balance = 0
                remaining_pool = pool.balance - balance
            else:
                remaining_balance = pool_diff
                remaining_pool = 0
            line_vals = {
                'date' : date.today(),
                'memo': self.memo,
                'reference': self.pool_report_id.id,
                'value_type': 'out',
                'pool_value': balance - remaining_balance,
                'value': remaining_pool,
                'pool_id': pool.id,
            }
            self.env['ssi_royalty.pool.line'].create(line_vals)
            # pool.update({'balance': line_vals['value']})
            paid_by_pool += (balance - remaining_balance)

            # create the vendor bill line
            total = remaining_balance + advance
            line_vals = {
                'product_id': product.id,
                'name': f"{self.pool_report_id.name} - {artist.name}",
                'account_id': 289,
                'quantity': 1,
                'price_unit': total,
            }
            move_rec.write({'invoice_line_ids': [(0,0,line_vals)]})

        # update record-level values
        self.pool_report_id.write({'paid_by_pool': self.pool_report_id.paid_by_pool + paid_by_pool})
        self.pool_report_id.write({'paid_by_vendor_bill': self.pool_report_id.paid_by_vendor_bill + self.journal_balance, 'move_id': move_rec.id})
        self.pool_report_id.write({'status': 'posted'})

        # notify user
        for royalty in self.pool_report_id.royalty_line_id:
            royalty.update({'is_report_approved': True})
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Payment Was Successfully Made'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
        return notification
    

    def action_make_payment(self):
        # create the vendor bill
        journal = self.vendor_journal_id
        account_date = date.today()
        payment_terms = self.licensor_id.property_supplier_payment_term_id
        move_values = {
            'journal_id': journal.id,
            'company_id': self.company_id.id,
            'partner_id': self.licensor_id.id,
            'move_type': 'in_invoice',
            'invoice_date': account_date,
            'ref': self.pool_report_id.name,
            'name': '/',
            'invoice_payment_term_id': payment_terms.id,
        }
        move_rec = self.env['account.move'].create(move_values)
        self.move_id = move_rec.id
        pro_id = self.env['ir.config_parameter'].sudo().get_param('royalty_product_item')
        product = self.env['product.product'].search([('id', '=', pro_id)])

        paid_by_pool = 0
        for artist in set(self.pool_payment_line_ids.mapped('artist_id')):
            lines = self.pool_payment_line_ids.filtered(lambda line: line.artist_id == artist)
            pool = self.env['ssi_royalty.pool'].search([('artist_id', '=', artist.id)], limit=1)
            if not pool:
                pool_vals = {
                    'artist_id': artist.id,
                    'licensor_id': self.licensor_id.id,
                    'balance': 0.0,
                }
                pool = self.env['ssi_royalty.pool'].create(pool_vals)
            advance = sum(lines.mapped('advance_payment'))
            balance = sum(lines.mapped('balance_to_pay')) - advance

            # add advance to pool
            if advance > 0:
                for advance_line in lines.filtered(lambda l: l.advance_payment > 0):
                    line_vals = {
                        'date': date.today(),
                        'memo': self.memo + " On Advance Payment",
                        'reference': self.pool_report_id.id,
                        'value_type': 'in',
                        'pool_value': advance_line.advance_payment,
                        'value': pool.balance + advance_line.advance_payment,
                        'pool_id': pool.id,
                        'art_id': advance_line.license_item_id.id,
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    # pool.update({'balance': line_vals['value']})

            for sale_line in lines.filtered(lambda l: not l.advance_payment > 0):
                if sale_line.license_item_id and sale_line.artist_id and sale_line.create_date:
                    pool_id = self.env['ssi_royalty.pool'].search([('artist_id', '=', sale_line.artist_id.id)])
                    pool_lines = self.env['ssi_royalty.pool.line'].search([('pool_id', '=', pool_id.id), ('value_type', '=', 'in'), ('first_sale_date', '=', False), ('art_id', '=', sale_line.license_item_id.id), ('create_date', '<=', sale_line.create_date)])
                    for pool_line in pool_lines:
                        pool_line.write({'first_sale_date': datetime.now()})

            # subtract total without advance from the pool
            pool_diff = balance - pool.balance
            if pool_diff <= 0:
                remaining_balance = 0
                remaining_pool = pool.balance - balance
            else:
                remaining_balance = pool_diff
                remaining_pool = 0
            line_vals = {
                'date' : date.today(),
                'memo': self.memo,
                'reference': self.pool_report_id.id,
                'value_type': 'out',
                'pool_value': balance - remaining_balance,
                'value': remaining_pool,
                'pool_id': pool.id,
            }
            self.env['ssi_royalty.pool.line'].create(line_vals)
            # pool.update({'balance': line_vals['value']})
            paid_by_pool += (balance - remaining_balance)

            # create the vendor bill line
            total = remaining_balance + advance
            line_vals = {
                'product_id': product.id,
                'name': f"{self.pool_report_id.name} - {artist.name}",
                'account_id': 289,
                'quantity': 1,
                'price_unit': total,
            }
            move_rec.write({'invoice_line_ids': [(0,0,line_vals)]})

        # update record-level values
        self.pool_report_id.write({'paid_by_pool': self.pool_report_id.paid_by_pool + paid_by_pool})
        self.pool_report_id.write({'paid_by_vendor_bill': self.pool_report_id.paid_by_vendor_bill + self.journal_balance, 'move_id': move_rec.id})
        self.pool_report_id.write({'status': 'posted'})

        # notify user
        for royalty in self.pool_report_id.royalty_line_id:
            royalty.update({'is_report_approved': True})
        # notification = {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': _('Payment Was Successfully Made'),
        #         'type': 'success',
        #         'next': {'type': 'ir.actions.act_window_close'},
        #     },
        # }
        # return notification
