{
    'name': "Base Module for Ecuadorian EDI",
    'version': '16.0.1.0',
    'depends': ['base', 'mail'],
    'author': "Marcelo Mora <marcelo.mora@accioma.com>",
    'category': 'Account & Finance',
    'description': """
    Base module for Ecuadorian EDI
    """,
    # data files always loaded at installation
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/l10n_ec_edi_document_views.xml',
        'data/cron.xml',
    ],
    'license': 'LGPL-3',
    # # data files containing optionally loaded demonstration data
    # 'demo': [
    #     'demo/demo_data.xml',
    # ],
    'category': 'base.module_category_accounting_localization',
    'application': True,
}
