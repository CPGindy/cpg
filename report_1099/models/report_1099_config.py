# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd.
# Copyright (C) 2021 (https://www.bistasolutions.com)
#
##############################################################################

import re

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Report1099Config(models.Model):
    _name = 'report.1099.config.partner'
    _rec_name = 'partner_id'
    _description = " Report Configuration Partner"

    income_list = [
        ('rent', '1. Rents'),
        ('royalty', '2. Royalties'),
        ('other', '3. Other Income'),
        ('federal_income_tax_withheld',
         '4. Federal income tax withheld'),
        ('fishing_boat_proceeds',
         '5. Fishing boat proceeds'),
        ('medical_and_health_care_payments',
         '6. Medical and health care payments'),
        ('non_emp_cmpr', '7. Nonemployee compensation'),
        ('sub_stitute_payments_in_lieu_of_dividends_or_interest',
         '8. Substitute payments in lieu of dividends or payments'),
        ('sale', '9. Direct Sales'),
        ('crop_insurance_proceeds', '10. Crop insurance proceeds'),
        ('11', '11. '), ('12', '12. '),
        ('excess_golden_perachute_payments',
         '13. Excess golden parachute payments'),
        ('gross_proceeds_paid_to_an_attomey',
         '14. Gross proceeds paid to an attorney'),
        ('section_409A_deferrals', '15a. Section 409A deferrals'),
        ('section_409A_income', '15.b. Section 409A income'),
        ('state_tax_withheld', '16. State tax withheld'),
        ("state_payers_state_no", "17. State/Payer's state no."),
        ('state_income', '18. State income')
    ]

    partner_id = fields.Many2one('res.partner', copy=False)
    is_1099 = fields.Boolean(string="Is 1099")
    ssn_ein = fields.Selection([('ssn', 'SSN'), ('ein', 'EIN')],
                               string='SSN/EIN No.')
    ssn_number = fields.Char('SSN Number', help='Format : XXX-XX-XXXX')
    ein_number = fields.Char('EIN Number', help='Format : XX-XXXXXXX')
    type_income = fields.Selection(income_list, string="Income Type",
                                   default='non_emp_cmpr',
                                   groups="report_1099.group_report_1099_vendor, \
                                report_1099.group_report_1099")
    type_co = fields.Selection([('individual_sole',
                                 'Individual/Sole Proprietor'),
                                ('c_corp', 'C Corporation'),
                                ('s_corp', 'S Corporation'),
                                ('partnership', 'Partnership'),
                                ('llc_c_corp', 'LLC - C Corp'),
                                ('llc_s_corp', 'LLC - S Corp'),
                                ('llc_partnership', 'LLC Partnership'),
                                ('dis_entity', 'Disregarded Entity')
                                ], string='Federal Tax Classification',
                               groups="report_1099.group_report_1099_vendor, \
                               report_1099.group_report_1099")
    legal_name = fields.Char('TIN Name',
                             groups="report_1099.group_report_1099_vendor, \
                             report_1099.group_report_1099")

    _sql_constraints = [('default_code_partner_id', 'unique (partner_id)',
                         'Partner should be unique!')]

    @api.onchange('is_1099', 'partner_id')
    def onchange_1099(self):
        for partner in self:
            if partner.partner_id and partner.legal_name != partner.partner_id.name:
                partner.legal_name = partner.partner_id.name

    def read(self, fields=None, load='_classic_read'):
        result = super(Report1099Config, self).read(fields, load=load)
        for record in result:
            if record.get('ssn_number'):
                record['ssn_number'] = \
                    'XXX-' + 'XX-' + str(record['ssn_number'])[-4:]
            if record.get('ein_number'):
                final = 'XX-XXX' + str(record['ein_number'])[-4:]
                record['ein_number'] = final
        return result

    @api.onchange('ssn_ein')
    def onchange_ssn_ein(self):
        if self.ssn_ein:
            if self.ssn_ein == 'ssn':
                self.ein_number = ''
            if self.ssn_ein == 'ein':
                self.ssn_number = ''

    @api.constrains('ssn_number', 'ein_number')
    def check_ssn_ein(self):
        for rec in self:
            if rec.ssn_ein == 'ssn' and rec.ssn_number:
                is_wrng_ssn = False
                if len(rec.ssn_number) != 11:
                    is_wrng_ssn = True
                if len(rec.ssn_number) == 11:
                    result = \
                        re.match(r"[0-9]{3}-[0-9]{2}-[0-9]{4}", rec.ssn_number)
                    if not result:
                        is_wrng_ssn = True
                if is_wrng_ssn:
                    raise ValidationError(_(
                        'Enter valid SSN number.\
                        \n Format: XXX-XX-XXXX.'))

            elif rec.ssn_ein == 'ein' and rec.ein_number:
                is_wrng_ien = False
                if len(rec.ein_number) != 10:
                    is_wrng_ien = True
                if len(rec.ein_number) == 10:
                    result = re.match(r"[0-9]{2}-[0-9]{7}", rec.ein_number)
                    if not result:
                        is_wrng_ien = True
                if is_wrng_ien:
                    raise ValidationError(_('Enter valid EIN number.\
                        \n Format: XX-XXXXXXX.'))

    @api.model
    def create(self, vals):
        """
        Override function to check ssn or ein number unique or not.
        :param vals:
        :return:
        """
        if vals.get('ssn_ein', False):
            ssn_ein_number = ""
            if vals.get('ssn_number', False):
                ssn_ein_number = vals['ssn_number']
            if vals.get('ein_number', False):
                ssn_ein_number = vals['ein_number']
            if ssn_ein_number:
                all_configs = self.search([])
                if all_configs and vals['ssn_ein'] == 'ssn' and ssn_ein_number in all_configs.mapped(
                    'ssn_number'):
                    raise ValidationError('The SSN No. must be unique!')
                if all_configs and vals['ssn_ein'] == 'ein' and ssn_ein_number in all_configs.mapped(
                        'ein_number'):
                    raise ValidationError('The EIN No. must be unique!')
        return super(Report1099Config, self).create(vals)

    def write(self, vals):
        """
        Override function to check ssn or ein number unique or not.
        :param vals:
        :return:
        """
        if vals.get('ssn_number', False) or vals.get('ein_number'):
            ssn_ein_number = ""
            if vals.get('ssn_number', False):
                ssn_ein_number = vals['ssn_number']
            if vals.get('ein_number', False):
                ssn_ein_number = vals['ein_number']
            if ssn_ein_number:
                all_configs = self.search([('id', '!=', self.id)])
                if all_configs and ssn_ein_number in all_configs.mapped(
                        'ssn_number'):
                    raise ValidationError('The SSN No. must be unique!')
                if all_configs and ssn_ein_number in all_configs.mapped(
                        'ein_number'):
                    raise ValidationError('The EIN No. must be unique!')
        return super(Report1099Config, self).write(vals)
