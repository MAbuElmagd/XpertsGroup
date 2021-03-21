
{
    "name": "itial Backend Theme V13",
    "summary": "itial Backend Theme V13",
    "version": "13.0.0.1",
    "category": "Theme/Backend",
    "website": "http://www.itial.tk",
	"description": """
		itial Backend theme for Odoo 13.0 community edition.
    """,
	'images':[
        'images/screen.png'
	],
    "author": "itial",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'web',
        'ow_web_responsive',

    ],
    "data": [
        'views/assets.xml',
		'views/res_company_view.xml',
		#'views/users.xml',
        #'views/sidebar.xml',
    ],

}
