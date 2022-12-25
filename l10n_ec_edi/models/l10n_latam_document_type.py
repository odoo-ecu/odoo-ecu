# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class L10NLatamDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'

    l10n_ec_edi_code = fields.Char("Edi Code")
    account_edi_format_id = fields.Many2one(
        'account.edi.format',
        'Account Edi Format')
    
    
    

