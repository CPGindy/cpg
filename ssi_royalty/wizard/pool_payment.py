from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date


class PoolPaymentLine(models.TransientModel):
    _name = 'pool.payment.line'
    
    artist_id = fields.Many2one('res.partner', string='Artist', readonly=True)
    licensor_id = fields.Many2one('res.partner', related="pool_payment_id.licensor_id", string='Licensor', readonly=True)
    available_balance = fields.Float(string='Available Pool Balance', readonly=True)
    balance_to_pay = fields.Float(string="Balance To Pay", readonly=True)
    memo = fields.Char(string='Memo')
    pool_report_id = fields.Many2one('ssi_royalty.report', string='Report')
    advance_payment = fields.Float(string='Advance Payment', readonly=True)
    journal_balance = fields.Float(string='Balance To Be Posted On Journal', compute='_compute_balance_to_be_posted')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    vendor_journal_id = fields.Many2one('account.journal', string='Journal')
    move_id = fields.Many2one('account.move', string='Vendor Bill', readonly=True)
    pool_payment_id = fields.Many2one('pool.payment', string="Payment Record")
    
    
    @api.depends('available_balance', 'balance_to_pay')
    def _compute_balance_to_be_posted(self):
        for rec in self:
            if rec.advance_payment and not rec.available_balance:
                if rec.balance_to_pay > rec.advance_payment:
                    remaining_balance = rec.balance_to_pay - rec.advance_payment
                    if remaining_balance < rec.advance_payment:
                        rec.journal_balance = rec.advance_payment
                    else:
                        rec.journal_balance = rec.balance_to_pay - rec.advance_payment
                else:
                    rec.journal_balance = rec.balance_to_pay
            elif not rec.available_balance or not rec.advance_payment:
                rec.journal_balance = rec.balance_to_pay
            elif rec.balance_to_pay < (rec.available_balance + rec.advance_payment):
                rec.journal_balance = 0.0
            elif rec.balance_to_pay > (rec.available_balance + rec.advance_payment):
                rec.journal_balance = rec.balance_to_pay - rec.available_balance - rec.advance_payment
            else:
                rec.journal_balance = 0.0
                
    def make_payment(self):
        for rec in self:
            search_pool = self.env['ssi_royalty.pool'].search([('artist_id', '=', self.artist_id.id)], limit=1)
            #if there is advance payment add the line balance to the pool balance,
            #create new pool records if the pool doesnot exist for that licensor
            if rec.advance_payment:
                if search_pool:
                    line_vals = {
                        'date': date.today(),
                        'memo': rec.memo + " On Advance Payment",
                        'value_type': 'in',
                        'pool_value': rec.advance_payment,
                        'value': rec.advance_payment + search_pool.balance,
                        'pool_id': search_pool.id
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    search_pool.update({'balance': line_vals['value']})
                else:
                    pool_val = {
                        'artist_id': rec.artist_id.id,
                        'licensor_id': rec.licensor_id.id,
                        'balance': 0.0
                    }
                    search_pool = self.env['ssi_royalty.pool'].create(pool_val)
                    line_vals = {
                        'pool_id': search_pool.id,
                        'date': date.today(),
                        'memo': rec.memo + " On Advance Payment",
                        'value_type': 'in',
                        'pool_value': rec.advance_payment,
                        'value': rec.advance_payment + search_pool.balance
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    search_pool.update({'balance': line_vals['value']})
            
            #if there is pool record for the licensors, deduct the line balance from pool balance
            #if balance to pay artist is more than pool balance deduct all the pool balance and 
            #post the remaining balance to vendor bills.
            out_from_advance = False
            if not rec.available_balance:
                if rec.balance_to_pay > rec.advance_payment:
                    out_from_advance = True
            if rec.balance_to_pay and (rec.available_balance or out_from_advance):
                balance = 0
                if out_from_advance:
                    if rec.balance_to_pay > rec.advance_payment:
                        remaining_balance = rec.balance_to_pay - rec.advance_payment
                        if remaining_balance > rec.advance_payment:
                            balance = rec.advance_payment
                        else:
                            balance = remaining_balance
                    else:
                        pass
                else:
                    if rec.balance_to_pay > (rec.available_balance + rec.advance_payment):
                        balance = rec.available_balance + rec.advance_payment
                    elif rec.balance_to_pay <= (rec.available_balance + rec.advance_payment):
                        balance = rec.balance_to_pay
                if search_pool:
                    line_vals = {
                        'date' : date.today(),
                        'memo': rec.memo,
                        'value_type': 'out',
                        'pool_value': balance,
                        'value': search_pool.balance - balance,
                        'pool_id': search_pool.id
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    
                    search_pool.update({'balance': search_pool.balance - balance})
                    rec.pool_report_id.update({'paid_by_pool':rec.pool_report_id.paid_by_pool+balance})
            #after checking and computing the balance to pay from available balance from pool, post the remaining
            #balance to the vendor bill
            if rec.journal_balance:
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
                line_vals = {
                    'product_id': product.id,
                    'name': self.pool_report_id.name,
                    'account_id': self.pool_report_id.royalty_line_id[0].account_id.id,
                    'quantity': 1,
                    'price_unit': self.journal_balance
                }
                move_rec.write({'invoice_line_ids': [(0,0,line_vals)]})
                self.pool_report_id.write({'paid_by_vendor_bill': self.pool_report_id.paid_by_vendor_bill + self.journal_balance, 'move_id': move_rec.id})
                
            self.pool_report_id.write({'status': 'posted'})
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
        for rec in self:
            if rec.advance_payment and not rec.available_balance:
                if rec.balance_to_pay > rec.advance_payment:
                    remaining_balance = rec.balance_to_pay - rec.advance_payment
                    if remaining_balance < rec.advance_payment:
                        rec.journal_balance = rec.advance_payment
                    else:
                        rec.journal_balance = rec.balance_to_pay - rec.advance_payment
                else:
                    rec.journal_balance = rec.balance_to_pay
            elif not rec.available_balance or not rec.advance_payment:
                rec.journal_balance = rec.balance_to_pay
            elif rec.balance_to_pay < (rec.available_balance + rec.advance_payment):
                rec.journal_balance = 0.0
            elif rec.balance_to_pay > (rec.available_balance + rec.advance_payment):
                rec.journal_balance = rec.balance_to_pay - rec.available_balance - rec.advance_payment
            else:
                rec.journal_balance = 0.0
                
    def make_payment(self):
        for rec in self:
            search_pool = self.env['ssi_royalty.pool'].search([('artist_id', '=', self.artist_id.id)], limit=1)
            #if there is advance payment add the line balance to the pool balance,
            #create new pool records if the pool doesnot exist for that licensor
            if rec.advance_payment:
                if search_pool:
                    line_vals = {
                        'date': date.today(),
                        'memo': rec.memo + " On Advance Payment",
                        'value_type': 'in',
                        'pool_value': rec.advance_payment,
                        'value': rec.advance_payment + search_pool.balance,
                        'pool_id': search_pool.id
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    search_pool.update({'balance': line_vals['value']})
                else:
                    pool_val = {
                        'artist_id': rec.artist_id.id,
                        'licensor_id': rec.licensor_id.id,
                        'balance': 0.0
                    }
                    search_pool = self.env['ssi_royalty.pool'].create(pool_val)
                    line_vals = {
                        'pool_id': search_pool.id,
                        'date': date.today(),
                        'memo': rec.memo + " On Advance Payment",
                        'value_type': 'in',
                        'pool_value': rec.advance_payment,
                        'value': rec.advance_payment + search_pool.balance
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    search_pool.update({'balance': line_vals['value']})
            
            #if there is pool record for the licensors, deduct the line balance from pool balance
            #if balance to pay artist is more than pool balance deduct all the pool balance and 
            #post the remaining balance to vendor bills.
            out_from_advance = False
            if not rec.available_balance:
                if rec.balance_to_pay > rec.advance_payment:
                    out_from_advance = True
            if rec.balance_to_pay and (rec.available_balance or out_from_advance):
                balance = 0
                if out_from_advance:
                    if rec.balance_to_pay > rec.advance_payment:
                        remaining_balance = rec.balance_to_pay - rec.advance_payment
                        if remaining_balance > rec.advance_payment:
                            balance = rec.advance_payment
                        else:
                            balance = remaining_balance
                    else:
                        pass
                else:
                    if rec.balance_to_pay > (rec.available_balance + rec.advance_payment):
                        balance = rec.available_balance + rec.advance_payment
                    elif rec.balance_to_pay <= (rec.available_balance + rec.advance_payment):
                        balance = rec.balance_to_pay
                if search_pool:
                    line_vals = {
                        'date' : date.today(),
                        'memo': rec.memo,
                        'value_type': 'out',
                        'pool_value': balance,
                        'value': search_pool.balance - balance,
                        'pool_id': search_pool.id
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    
                    search_pool.update({'balance': search_pool.balance - balance})
                    rec.pool_report_id.update({'paid_by_pool':rec.pool_report_id.paid_by_pool+balance})
            #after checking and computing the balance to pay from available balance from pool, post the remaining
            #balance to the vendor bill
            if rec.journal_balance:
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
                line_vals = {
                    'product_id': product.id,
                    'name': self.pool_report_id.name,
                    'account_id': self.pool_report_id.royalty_line_id[0].account_id.id,
                    'quantity': 1,
                    'price_unit': self.journal_balance
                }
                move_rec.write({'invoice_line_ids': [(0,0,line_vals)]})
                self.pool_report_id.write({'paid_by_vendor_bill': self.pool_report_id.paid_by_vendor_bill + self.journal_balance, 'move_id': move_rec.id})
                
            self.pool_report_id.write({'status': 'posted'})
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
