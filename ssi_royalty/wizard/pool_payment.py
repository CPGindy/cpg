from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date


class PoolPayment(models.TransientModel):
    _name = 'pool.payment'
    
    licensor_id = fields.Many2one('res.partner', string='Licensor', readonly=1)
    available_balance = fields.Float(string='Available Pool Balance', readonly=1)
    balance_to_pay = fields.Float(string="Balance To Pay", readonly=1)
    balance_amount = fields.Float(string='Payment Amount', required=True)
    memo = fields.Char(string='Memo')
    pool_report_id = fields.Many2one('ssi_royalty.report', string='Report')
    
    
    def make_payment(self):
        for rec in self:
            if not rec.available_balance:
                raise UserError(_('Licensor Does Not Have Any Pool Balance'))
            else:
                if rec.balance_amount <= 0:
                    raise UserError(_('Payment Amount Must Be Positive Amount'))
                elif rec.balance_amount > rec.balance_to_pay:
                    raise UserError(_('Payment Balance Can Not Be More Than Actual Balance To Pay'))
                elif rec.balance_amount > rec.available_balance:
                    raise UserError(_('Pool Doesnot Has Enough Balance'))
                search_pool = self.env['ssi_royalty.pool'].search([('licensor_id', '=', self.licensor_id.id)], limit=1)
                if search_pool:
                    line_vals = {
                        'date' : date.today(),
                        'memo': rec.memo,
                        'value_type': 'out',
                        'value': rec.balance_amount,
                        'pool_value': search_pool.balance - rec.balance_amount,
                        'pool_id': search_pool.id
                    }
                    self.env['ssi_royalty.pool.line'].create(line_vals)
                    
                    search_pool.update({'balance': search_pool.balance - rec.balance_amount})
                    if rec.balance_to_pay == rec.balance_amount:
                        rec.pool_report_id.update({'status': 'paid','paid_by_pool':rec.pool_report_id.paid_by_pool+rec.balance_amount})
                    elif rec.balance_to_pay > rec.balance_amount:
                        rec.pool_report_id.update({'status': 'partial_paid', 'paid_by_pool':rec.pool_report_id.paid_by_pool+rec.balance_amount})
                else:
                    raise UserError(_('No Pool Record Found For This Licensor'))