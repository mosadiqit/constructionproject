{
    'name': 'Payroll Management',
    'version': '12.0.1.0.0',
    'category': 'Project Managements',
    'summary': 'This model Adds financial situation of employees',
    'author': 'Mohamed sadiq',
    'depends': ['base', 'mail', 'product', 'hr', 'sdq_project_costs', 'hr_holidays'],
    'demo': [],
    'data': [
        #'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/burner.xml',
        'views/menu.xml'
       
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

