# Copyright 2021 Akretion (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class L10N_LatamIdentificationType(models.Model):
    _inherit = 'l10n_latam.identification.type'

    l10n_ec_id_edi_code = fields.Char("EC Identification EDI Code", size=2)
    
    

