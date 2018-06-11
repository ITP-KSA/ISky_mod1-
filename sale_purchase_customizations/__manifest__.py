# -*- coding: utf-8 -*-
{
    'name': "Sale/Purchase Customizations",
    'version': '0.1',
    'author': "",
    'summary': """Sale/Purchase Customizations""",
    'category': '',
    'description': """
Sale/Purchase Customizations
====================================

Add customizations to Sale and Purchase cycles.
    """,
    'website': "",
    'depends': [
        'base',
        'account',
        'sale_management',
        'purchase',
        'stock',
        'project',
        'sale_timesheet',
    ],
    'data': [
        'security/security.xml',
        'views/project_views.xml',
        'views/product_views.xml',
        'views/res_users_views.xml',
        'views/sale_order_line_tree.xml',
        'views/account_invoice_lines_tree.xml',
        'views/purchase_order_lines_tree.xml',
        'views/stock_move_tree.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/stock_picking_view.xml',
        'views/custom_external_layout.xml',
        'views/report_quotation.xml',
        'views/report_invoice.xml',
        'reports/report_stock_picking.xml',
        'reports/sale_report_inherit.xml',
        'reports/report_account_invoices.xml',
        # Menu Item
        'views/menuitems.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
}
