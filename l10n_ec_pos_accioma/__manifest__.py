# -*- encoding: utf-8 -*-
# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "POS Ecuador",
    "summary": "Point of Sale localization for Ecuador",
    "version": " 14.0.1.0.0",
    "category": "Point of Sale",
    "website": "accioma.com",
    "author": " Accioma",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "l10n_ec",
    ],
    "data": [
        "views/pos_assets.xml",
    ],
    "demo": [
    ],
    "qweb": [
        "static/src/xml/receipt.xml",
    ],
    "installable": False,
}
