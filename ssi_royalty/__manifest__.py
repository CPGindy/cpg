
# Systems Services, Inc.

{
    'name': 'Royalty',

    'summary': """
        Module for calculating royalties for artists based on their products sale""",

    'description': """
       Track and computes royalty payments for artwork sales
    """,

    'author': "Bishal Ghimire - Systems Services Inc",
    'website':  "http://www.ssibtr.com",
    'category': 'SSI',
    'version': '0.1.0',

    'depends': ['base', 'product','account', 'mail', 'account', 'ssi_custom'],

    'data': [
        'security/ir.model.access.csv',

        'views/royalty_views.xml',
        'views/license_views.xml',
        'views/license_item_views.xml',
        'views/license_product_views.xml',
        'views/license_for_views.xml',
        'views/artist_royalty_pool_views.xml',
        'views/product_views.xml',
        'views/royalty_report_views.xml',
        'views/license_item_pool_views.xml',
        'views/account_move_views.xml',

        'data/ir_sequence_data.xml',
        'data/ir_config_parameter.xml',
        'data/license_category_data.xml',
        'data/royalty_email_template.xml',

        'wizard/pool_payment.xml',

        'reports/royalty_report.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'cloc_exclude': [
        "./**/*"
    ]
}
