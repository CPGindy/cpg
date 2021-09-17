from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date


class PoolPaymentLine(models.TransientModel):
    _name = 'pool.payment.line'

    artist_id = fields.Many2one('res.partner', string='Artist', readonly=True)
    available_balance = fields.Float(string='Available Pool Balance', readonly=True)
    balance_to_pay = fields.Float(string="Balance To Pay", readonly=True)
    advance_payment = fields.Float(string='Advance Payment', readonly=True)
    pool_payment_id = fields.Many2one('pool.payment', string="Payment Record")


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
        move_values = {
            'journal_id': journal.id,
            'company_id': self.company_id.id,
            'partner_id': self.licensor_id.id,
            'move_type': 'in_invoice',
            'invoice_date': account_date,
            'ref': self.pool_report_id.name,
            'name': '/',
        }
        move_rec = self.env['account.move'].create(move_values)
        self.move_id = move_rec.id
        pro_id = self.env['ir.config_parameter'].get_param('royalty_product_item')
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
                line_vals = {
                    'date': date.today(),
                    'memo': self.memo + " On Advance Payment",
                    'value_type': 'in',
                    'pool_value': advance,
                    'value': pool.balance + advance,
                    'pool_id': pool.id,
                }
                self.env['ssi_royalty.pool.line'].create(line_vals)
                pool.update({'balance': line_vals['value']})

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
                'value_type': 'out',
                'pool_value': balance - remaining_balance,
                'value': remaining_pool,
                'pool_id': pool.id,
            }
            self.env['ssi_royalty.pool.line'].create(line_vals)
            pool.update({'balance': line_vals['value']})
            paid_by_pool += (balance - remaining_balance)

            # create the vendor bill line
            total = remaining_balance + advance
            line_vals = {
                'product_id': product.id,
                'name': f"{self.pool_report_id.name} - {artist.name}",
                'account_id': self.pool_report_id.royalty_line_id[0].account_id.id,
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
