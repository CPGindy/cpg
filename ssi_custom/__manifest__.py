# Systems Services, Inc.

{
    'name': "SSI Custom",

    'summary': """
        Module is for customizing base Odoo functionality for CPG""",

    'description': """
        Customizes base Odoo functionalities and add new one if applies
    """,

    'author': "Bishal Ghimire - Systems Services Inc",
    'website':  "http://www.ssibtr.com",
    'category': 'SSI',
    'version': '0.1.0',
    'depends': ['base', 'stock', 'delivery'],

    'data': [
        'report/ssi_stock_picking_report.xml',
        'views/stock_picking_views.xml',
        'views/delivery_carrier_views.xml',
    ],
    'demo': [
    ],
    'cloc_exclude': [
        "./**/*"
    ]
}
