# -*- coding: utf-8 -*-
{
    'name': "O.T.E. - Ecuador",
    'summary': """Ecuador's Geopolitical Information.""",
    'version': '17.0.1.0.0',
    'author': "Odoo Community Association (OCA)",
    'maintainer': 'Accioma',
    'website': 'http://www.accioma.com',
    'license': 'AGPL-3',
    'category': 'Localization',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_partner.xml',
        'views/res_company.xml',
        'data/res.country.state.csv',
        'data/l10n_ec_ote.canton.csv',
        'data/l10n_ec_ote.parish.csv',
        'data/res_country.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
