# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    l10n_ec_edi_issuing_type = fields.Selection([
        ('1', 'Normal')
        ], "Issuing Type",
        default='1',
        config_parameter='l10n_ec_edi_accioma.issuing_type'
        )

    l10n_ec_edi_environment_type = fields.Selection([
        ('1', 'Testing'),
        ('2', 'Production'),
        ], "Environment Type", default='1',
        config_parameter='l10n_ec_edi_accioma.environment_type'
        )


