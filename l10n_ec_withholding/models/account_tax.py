# -*- encoding: utf-8 -*-
# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class AccountTax(models.Model):
    _inherit = 'account.tax'

    withhold_amount = fields.Float("Withholding Amount", required=False, digits=(16, 4), default=0.0)

