# -*- coding: utf-8 -*-
{
    'name': "FAQ",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "M.Abuelmagd",
    'website': "http://www.itial.tk",
'images': [
'static/src/img/faq.png'
],
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','mail'],

    'data': [
        'views/views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
