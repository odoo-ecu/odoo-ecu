# Copyright 2021 Accioma (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Ecuador EDI",
    "summary": "SRI Electronic Data Interchange",
    "version": "16.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "accioma.com",
    "author": "Accioma",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": ["ecedi"],
        "bin": [],
    },
    "depends": [
        "account_edi",
        "l10n_ec_withholding",
        "l10n_ec_clearance",
        "partner_contact_tradename",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/account_move_views.xml",
        "views/l10n_latam_document_type_view.xml",
        "data/account_edi_format_data.xml",
        "data/l10n_latam_document_type_data.xml",
        "data/template_invoice.xml",
        "data/l10n_latam_identification_type_data.xml",
        "data/account_tax_group_data.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
