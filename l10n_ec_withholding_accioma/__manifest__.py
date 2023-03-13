# -*- coding: utf-8 -*-
{
    'name': "Ecuador | Withholding",

    'summary': """
        Whithholding taxes for Ecuador
    """,

    'description': """
    Withholding for Ecuador:
    - Income whithholding taxes
    - Vat whitholging taxes
    """,

    'author': "Accioma",
    'website': "http://www.accioma.com",

    'category': 'Accounting Finance',
    'version': '16.0.1.0.0',

    'depends': ['l10n_ec', ],
    'data': [
        'views/withholding_views.xml',
        'views/account_tax_views.xml',
        'data/template_withholding.xml',
    ],
}
