# -*- coding: utf-8 -*-
{
    'name': "Hospital Management System(Customized)",

    'summary': """
        A module that extends the Hospital Management System(basic_hms)    
    """,

    'description': """
        A module that extends the Hospital Management System(basic_hms)
    """,

    'author': "Afya Now",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/17.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'basic_hms'],

    # always loaded
    'data': [
        # 'security/groups.xml',
        # 'security/ir.model.access.csv',
        # 'data/ir_sequence_data.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,    
}
