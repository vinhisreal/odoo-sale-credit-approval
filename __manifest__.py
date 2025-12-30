# -*- coding: utf-8 -*-
{
    'name': "Sale Credit Limit & Approval",

    'summary': "Control credit limit and approval workflow for large Sales Orders",

    'description': """
Enforce customer credit limits and require approval for large Sales Orders.
    """,

    'author': "Nguyen Quang Vinh",
    'website': "https://github.com/vinhisreal",

    'category': 'Sales',
    'version': '1.0',

    # modules required
    'depends': [
        'sale',
        'account'
    ],

    # always loaded
    'data': [
        'security/security_groups.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
    ],

    'installable': True,
    'application': False,
}
