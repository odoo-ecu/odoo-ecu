# Copyright 2021 Akretion (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    partner_tradename = fields.Char("Tradename", related="partner_id.tradename")
    

    

