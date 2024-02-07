# Copyright 2023 Accioma (https://accioma.com).
# @author marcelomora <marcelo.mora@accioma.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re
from datetime import datetime as dt
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.l10n_ec_edi_base_accioma.models import base_edi

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ec_edi_in_number = fields.Char("Authorization Number")
    is_l10n_ec_edi_in_number_valid = fields.Boolean(string='Is Authorization Number Valid?', compute='l10n_ec_edi_in_number_valid')

    def l10n_ec_edi_in_number_valid(self):
        for move in self:
            move.is_l10n_ec_edi_in_number_valid = False
            if not self.l10n_ec_edi_in_number:
                move.is_l10n_ec_edi_in_number_valid = True

            if self.l10n_ec_edi_in_number and bool(re.match(r'^\d{49}$', self.l10n_ec_edi_in_number)) and\
                    base_edi.compute_check_digit(self.l10n_ec_edi_in_number[:-1]) == int(self.l10n_ec_edi_in_number[-1:]) and\
                    self.l10n_ec_edi_in_number[23] == '2' and\
                    self.l10n_latam_document_type_id.code == self.l10n_ec_edi_in_number[8:10]: # Environment and Document type match validation

                move.is_l10n_ec_edi_in_number_valid = True

            if self.l10n_ec_edi_in_number and bool(re.match(r'^\d{10}$', self.l10n_ec_edi_in_number)):
                move.is_l10n_ec_edi_in_number_valid = True

    @api.onchange('l10n_ec_edi_in_number')
    def _l10n_ec_edi_in_number_change(self):
        """Decompose access key, obtain document values and fill the
        fields according to it"""

        # Check digit validation
        if self.l10n_ec_edi_in_number and bool(re.match(r'^\d{49}$', self.l10n_ec_edi_in_number)) and\
                    base_edi.compute_check_digit(self.l10n_ec_edi_in_number[:-1]) == int(self.l10n_ec_edi_in_number[-1:]):

    #
            # Document date
            self.invoice_date = dt.strptime(self.l10n_ec_edi_in_number[:8], "%d%m%Y")
    #
             # Get the supplier
            partners = self.env['res.partner'].search([('vat', '=', self.l10n_ec_edi_in_number[10:23])])

            if partners:
                self.partner_id = partners[0]
    #
            # Get the document type
    #
            # Document number
            self.l10n_latam_document_number = "%s-%s-%s" % (self.l10n_ec_edi_in_number[24:27], self.l10n_ec_edi_in_number[27:30], self.l10n_ec_edi_in_number[30:39])



