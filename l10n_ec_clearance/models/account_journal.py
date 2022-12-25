# -*- encoding: utf-8 -*-
# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    l10n_ec_shop_address_id = fields.Many2one(
        'res.partner',
        'Shop Address')

    l10n_ec_company_partner_id = fields.Many2one(
        'res.partner',
        'Company Partner',
        related="company_id.partner_id"
    )

    l10n_ec_wth_seq_id = fields.Many2one(
        string="Withholding Sequence",
        comodel_name="ir.sequence",
        ondelete="restrict",
        help="Sequence for withholding on purchasing.",
    )

