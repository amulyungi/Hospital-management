# -*- coding: utf-8 -*-
{
    'name': "Know Your Customers",

    'summary': """
        A module for storing KYC details
    """,

    'description': """
        A module for storing KYC details
    """,

    'author': "Escrow",
    'website': "#",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/settings.xml',
        'views/customer.xml',
        'views/menu.xml',
        'views/res_partner.xml',
        'wizard/know_your_customer.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,     
}
