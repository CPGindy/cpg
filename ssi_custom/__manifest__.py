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
    'depends': ['base', 'stock', 'delivery', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'report/ssi_stock_picking_report.xml',
        'views/stock_picking_views.xml',
        'views/delivery_carrier_views.xml',
        'views/product_product_views.xml',
        'views/sku_lookup_views.xml',
        # 'report/ssi_invoice_report.xml'
    ],
    'demo': [
    ],
    'cloc_exclude': [
        "./**/*"
    ]
}
