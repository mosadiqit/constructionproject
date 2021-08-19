# -*- coding: utf-8 -*-
{
    'name': "sdq_project_costs",

    'summary': """
        This model the total funds needed to complete the project or work that consists of a Direct Cost and Indirect Cost.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Mohamed Sadiq",
    'website': "https://www.sadiq.ma",

    # category
    # version
    'category': 'Project Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'product', 'uom', 'stock', 'hr', 'fleet', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'data/data.xml',
        'data/ir_sequence.xml',
        # 'views/vehicle_renting_view.xml',
        # 'views/project_units.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
