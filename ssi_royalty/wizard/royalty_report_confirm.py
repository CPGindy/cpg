from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime


class RoyaltyReportConfirm(models.TransientModel):
    _name = 'royalty.report.confirm'


    royalty_ids = fields.Many2many('ssi_royalty.ssi_royalty', string='Royalties')
    report_date = fields.Date(string='Report Date', default=fields.Date.today)

    def generate_reports(self):
        for rec in self.royalty_ids.filtered(lambda a: not a.is_report_approved):
            if rec.licensor_id:
                royalty_line = [(6, 0, [rec.id])]
                search_report = self.env['ssi_royalty.report'].search([('licensor_id', '=', rec.licensor_id.id), ('status', '=', 'draft')], limit=1)
                if search_report and search_report.status not in ['posted', 'paid']:
                    search_report.update({'royalty_line_id' : [(4, rec.id)]})
                else:
                    header_vals = {
                        'status': 'draft',
                        'licensor_id': rec.licensor_id.id,
                        'report_date': self.report_date,
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