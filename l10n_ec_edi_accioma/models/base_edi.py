# Copyright 2021 Accioma (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import randint
from odoo import api, models


class EdiMixin(models.AbstractModel):
    _name = 'ec.edi.mixin'
    _description = 'Electronic documents base class'

    @api.model
    def compute_check_digit(
            self, number,
            factors='765432765432765432765432765432765432765432765432'):
        # Electronic voucher data sheet, p. 4
        # Modulus 11 checking method
        if not all([d.isdigit() for d in number]):
            return -1
        cd = 11 - sum([int(x[0])*int(x[1]) for x in zip(number, factors)]) % 11
        if cd == 11: return 0 # when check digit is 11 return 0. Data sheet p. 4
        if cd == 10: return 1 # when check digit is 10 return 1. Data sheet p. 4
        return cd

    @api.model
    def is_valid(self, number):
        if not all([d.isdigit() for d in number]):
            return False
        return self.compute_check_digit(number) == int(number[-1])

    @api.model
    def compute_numeric_code(self):
        return "".join([str(randint(0, 9)) for i in range(5)])


