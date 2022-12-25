# Copyright 2021 Accioma (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class EdiMixin(models.AbstractModel):
    _name = 'edi.mixin'
    _description = 'Electronic documents base class'

    l10n_ec_access_key = fields.Char("Access Key", store=False)

