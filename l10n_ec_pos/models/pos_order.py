# -*- encoding: utf-8 -*-
# Copyright 2022 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    l10n_ec_authorization = fields.Char('Authorization')
    l10n_ec_internal_number = fields.Char('Internal Number')
    
class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    l10n_ec_payment_method = fields.Char('Payment Method')
    


