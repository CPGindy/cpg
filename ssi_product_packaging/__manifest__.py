# Systems Services, Inc.

{
    'name': "SSI Product Packaging",

    'summary': """
        Module is for enhancing the existing base product packing with better storage and product specification options""",

    'description': """
        Enhance the existing product packing module
    """,

    'author': "Bishal Ghimire - Systems Services Inc",
    'website':  "http://www.ssibtr.com",
    'category': 'SSI',
    'version': '0.1.0',
    'depends': ['base', 'product', 'crm', 'sale', 'purchase', 'mrp', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_packaging_views.xml',
        'report/ssi_product_packaging_report.xml',
        'report/ssi_product_packaging_templates.xml',
        # 'report/ssi_invoice_report_inherit.xml',
        # 'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/mrp_bom_views.xml',
        'views/ssi_packaging_type_views.xml',
        'views/sku_lookup_views.xml',
        'views/product_product_views.xml',
        'data/packaging_type.xml',
        'report/ssi_purchase_order_report.xml',
        'report/ssi_sale_order_report.xml',
    ],
    'demo': [
    ],
    'cloc_exclude': [
        "./**/*"
    ]
}
