from odoo import api, fields, models, _
from odoo.exceptions import UserError

from datetime import datetime


class RoyaltyReportPDF(models.Model):
    _name = "royalty.report.pdf"
    _description = "PDF Royalty Reports"

    def print_server_action(self, context=None):
        datas = self.env['royalty.report.pdf'].search([]).ids
        if not datas:
            datas = self.create(dict())
        return self.env.ref('ssi_royalty.quarterly_royalty_report_pdf').report_action(datas)

    def generate_quarterly_report(self):
        now = datetime.now()
        quarter_start = (int(now.month) // 3) * 3
        quarter_end = quarter_start + 3
        reports = self.env['ssi_royalty.report'].search(
            [('date_year', '=', now.year), ('date_month', '>', quarter_start), ('date_month', '<=', quarter_end)])
        return reports
