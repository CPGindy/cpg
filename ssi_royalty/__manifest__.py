  
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
    'version': '0.1',

    'depends': ['base', 'product','account', 'mail'],

    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/royalty_views.xml',
        'views/license_views.xml',
        'views/license_item_views.xml',
        'views/license_product_views.xml',
        'views/license_for_views.xml',
        'views/artist_royalty_pool_views.xml',
        'views/product_views.xml',
        'views/royalty_report_views.xml',
        'data/ir_config_parameter.xml',
        'data/license_category_data.xml',
        'views/license_item_pool_views.xml',
        'wizard/pool_payment.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}