# Copyright 2021 Accioma (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ec_msg_taxpayer = fields.Char("Message Taxpayer")
    l10n_ec_msg_small_company = fields.Char("Message Small Company")

    l10n_ec_regime_microenterprise = fields.Boolean("Regime Microenterprise")
    l10n_ec_retention_agent = fields.Char("Retention Agent")
    
    l10n_ec_enforced_accounting = fields.Boolean("Enforced Accounting")
    l10n_ec_special_taxpayer = fields.Boolean("Special Tax Payer")
