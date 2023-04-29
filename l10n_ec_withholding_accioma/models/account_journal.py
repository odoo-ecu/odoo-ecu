# -*- encoding: utf-8 -*-

from odoo import _, api, fields, models, tools

class AccountJournal(models.Model):

    _inherit = 'account.journal'

    l10n_ec_withholding_type = fields.Selection([
        ('in_withholding', 'Receives Withholding'),
        ('out_withholding', 'Issues withholding')],
        'Withholding Type', help="Set the type of withholding that applies "
        "for the given journal")

    @api.depends('type', 'country_code', 'l10n_latam_use_documents', 'l10n_ec_withholding_type')
    def _compute_l10n_ec_require_emission(self):
        for journal in self:
            if journal.l10n_ec_withholding_type == 'out_withholding' and journal.country_code == 'EC':
                journal.l10n_ec_require_emission = True
            else:
                journal.l10n_ec_require_emission = journal.type == 'sale' and journal.country_code == 'EC' and journal.l10n_latam_use_documents
