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
        "fleet",
        "l10n_ec_edi_base_accioma",
        "l10n_latam_invoice_document"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
        "views/waybill_views.xml",
        "views/account_move_views.xml",
        "views/transport_views.xml",
        "data/template_waybill.xml",
    ],
    "license": "AGPL-3",
}
