# -*- coding: utf-8 -*-
{
    'name': "Product Sample",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "IT Principles",
    'website': "http://www.itp-ksa.com",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['sale_management', 'stock'],
    'data': [
        'data/base_automation.xml',
        'data/product_sample_sequence.xml',
        'views/sale_order_view.xml',
    ],
}
