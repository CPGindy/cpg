# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd.
# Copyright (C) 2021 (https://www.bistasolutions.com)
#
##############################################################################

{
    "name": "Report 1099",
    "summary": "Report 1099",
    "version": '14.0.1.0.0',
    "description": """
Report 1099
====================
This module help to print Report 1099.
The 1099 form is a series of documents the Internal Revenue Service (IRS) refers to as "information returns." 
There are several different 1099 forms that report the various types of income you may receive throughout the year 
other than the salary your employer pays you.
    """,
    "category": "Reporting",
    'license': 'OPL-1',
    "website": "https://www.bistasolutions.com",
    "author": "Bista Solutions Pvt. Ltd.",
    "depends": ['base', 'purchase', 'account',
                ],
    "data": [
        'security/report_1099_security.xml',
        'security/ir.model.access.csv',
        'views/report_1099_config_view.xml',
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
        'views/report_1099_view.xml',
        'wizard/wiz_report_1099_view.xml',
        'views/account_payment_view.xml',
        'report/report_1099_reg.xml',
        'report/report_1099_template.xml'
    ],
    'installable': True,
    'currency': 'USD',
    'price': 299.00,
    'application': False,
    'auto_install': False,

}
