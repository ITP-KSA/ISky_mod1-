# -*- coding: utf-8 -*-

{
    'name': 'Sale Order line with sequence number',
    'version': '11.0.1.0.0',
    "summary": "Adds sequence field on Sale Order lines to manage its order.",
    'category': 'Sale',
    'website': '',
    'depends': ['sale_purchase_customizations'],
    'data': ['views/sale_order_line_view.xml'],
    # 'post_init_hook': 'post_init_hook',
    'license': 'AGPL-3',
    'installable': True,
}
