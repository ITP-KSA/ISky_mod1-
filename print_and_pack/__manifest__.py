# -*- coding: utf-8 -*-
{
    'name': "Printing and Packing",
    'summary': """
        Creates PPA on confirmation of sale order.""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'sale',
    'version': '0.1',
    'depends': ['sale_stock', 'sale_purchase_customizations',
                'product_sample'],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/ppa_sequence.xml',
        'views/print_and_pack_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
    ],
}
