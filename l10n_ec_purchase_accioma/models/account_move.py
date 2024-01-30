# Copyright 2023 Accioma (https://accioma.com).
# @author marcelomora <marcelo.mora@accioma.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime as dt
from odoo import _, api, fields, models
from odoo.addons.l10n_ec_edi_base_accioma.models import base_edi

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ec_edi_in_number = fields.Char("Authorization Number")

    @api.onchange('l10n_ec_in_auth_number')
    def _l10n_ec_ed_auth_number_change(self):
        """Decompose access key, obtain document values and fill the
        fields according to it"""

        # Check digit validation
        vd = None
        vd = base_edi.compute_check_digit(self.l10n_ec_in_auth_number[:-1])
        _logger.info(vd)
    #
    #
    #     # Environment validation
    #
    #     # Document date
    #     # self.invoice_date = dt.strptime(self.l10n_ec_in_auth_number[:8], "%d%m%Y")
    #
    #     # Get the supplier
    #
    #     # Get the document type
    #
        # Document number



