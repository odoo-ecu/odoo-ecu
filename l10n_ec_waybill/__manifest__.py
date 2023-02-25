{
    "name": "Waybill Ecuador",
    "summary": "Waybill localization for Ecuador",
    "version": "14.0.1.0.2",
    "category": "Stock",
    "website": "accioma.com",
    "author": "Accioma",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_stock",
        "l10n_latam_invoice_document",
        "fleet",
        "l10n_ec_edi",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
        "views/waybill_views.xml",
        "data/template_waybill.xml",
    ],
}
