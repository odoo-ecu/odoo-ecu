{
    "name": "Ecuadorian Localization SRI Clearance Management",
    "summary": "- Manages SRI clearances for shops and places.\n"
               "- Validates purchasing authorization numbers.\n",
    "version": "14.0.1.0.0",
    "category": "Accounting and Finance",
    "website": "accioma.com",
    "author": "Accioma",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account", "l10n_latam_invoice_document",
    ],
    "data": [
        "views/account_journal.xml",
        "views/account_move_view.xml",
    ],
}
