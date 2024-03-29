# Copyright 2023 Accioma (https://accioma.com).
# @author marcelomora <marcelo.mora@accioma.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Ecuador Localization Purchasing",
    "summary": "Adds electronic authorization number and validation",
    "version": " 16.0.1.0.0",
    "category": "Localization",
    "website": "accioma.com",
    "author": " Accioma",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "l10n_latam_invoice_document",
        "l10n_ec_edi_base_accioma",
    ],
    "data": [
        "views/account_move_views.xml"

    ],
}
