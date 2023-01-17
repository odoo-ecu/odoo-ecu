# Copyright 2021 Akretion (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    l10n_ec_edi_group_code = fields.Char("EDI Code")
    l10n_ec_edi_percentage_code = fields.Char("EDI Percentage Code")
    l10n_ec_edi_percentage = fields.Float("Tax Percentage (Reports)")




