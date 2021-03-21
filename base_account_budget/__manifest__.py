
{
    'name': 'Odoo 13 Budget Management',
    'version': '13.0.1.1.0',
    'summary': """ Budget Management for Odoo 13 Community Edition. """,
    'description': """ This module allows accountants to manage analytic and budgets.

     Once the Budgets are defined (in Accounting/Accounting/Budgets), the Project Managers
     can set the planned amount on each Analytic Account.

     The accountant has the possibility to see the total of amount planned for each
     Budget in order to ensure the total planned is not greater/lower than what he
     planned for this Budget. Each list of record can also be switched to a graphical
     view of it.

     Three reports are available:

     1. The first is available from a list of Budgets. It gives the spreading, for
     these Budgets, of the Analytic Accounts.
     2. The second is a summary of the previous one, it only gives the spreading,
     for the selected Budgets, of the Analytic Accounts.
     3. The last one is available from the Analytic Chart of Accounts. It gives
     the spreading, for the selected Analytic Accounts of Budgets.
     Odoo 13 Budget Management,Odoo 13, Odoo 13 Budget, Odoo 13 Accounting,
     Odoo 13 Account,Budget Management, Budget""",
    'category': 'Accounting',
    'author': ' Odoo SA,M. Abuelmagd',
    'website': "https://www.itial.tk",
    'company': 'itial',
    'maintainer': 'itial',
    'depends': ['base', 'account', 'base_accounting_kit'],
    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
    ],
    'images': ['static/description/banner.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
