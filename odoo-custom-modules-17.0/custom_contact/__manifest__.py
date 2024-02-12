# -*- coding: utf-8 -*-
{
    'name': "Customized Contacts",

    'summary': """
        A module that extends Contacts
    """,

    'description': """
        A module that extends Contacts
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','auth_signup','mail'],

    # always loaded
    'data': [
        # 'security/groups.xml',
        # 'security/ir.model.access.csv',
        # 'data/ir_sequence_data.xml',
        'views/res_partner.xml',
        'views/settings.xml',
        'views/security_notification_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,    
}
