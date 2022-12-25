# -*- encoding: utf-8 -*-
# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ecedi import accesskey
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ec_clearance_number = fields.Char("Clearance Number")

    @api.constrains('l10n_ec_clearance_number')
    def _check_clearance_number(self):
        for move in self:
            if not move.l10n_ec_clearance_number:
                return True
            if not accesskey.is_valid(move.l10n_ec_clearance_number) \
                   and len(move.l10n_ec_clearance_number) != 10:
                raise ValidationError(_("Incorrect access key or clearance number"))

