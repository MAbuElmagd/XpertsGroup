
{
    'name': 'Payroll Advanced Features',
    'summary': 'Payroll Advanced Features For Odoo 13 Community.',
    'description': 'Payroll Advanced Features For Odoo 13 Community, payroll, odoo13, payroll report, payslip report',
    'category': 'Generic Modules/Human Resources',
    'version': '13.0.1.0.0',
    'author': ' Odoo SA,M. Abuelmagd',
    'website': "https://www.itial.tk",
    'company': 'itial',
    'maintainer': 'itial',
    'depends': [
        'hr_payroll_community', 'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip.xml',
        'views/res_config_settings_views.xml',
        'data/payslip_mail_template.xml',
        'wizard/hr_payslip_mass_confirm.xml',
        'report/hr_payslip_report.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
