# Copyright 2021 Accioma (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import randint

def compute_check_digit(
        number,
        factors='765432765432765432765432765432765432765432765432'):
    # Electronic voucher data sheet, p. 4
    # Modulus 11 checking method
    if not all([d.isdigit() for d in number]):
        return -1
    cd = 11 - sum([int(x[0])*int(x[1]) for x in zip(number, factors)]) % 11
    if cd == 11: return 0 # when check digit is 11 return 0. Data sheet p. 4
    if cd == 10: return 1 # when check digit is 10 return 1. Data sheet p. 4
    return cd

def is_valid(number):
    if not all([d.isdigit() for d in number]):
        return False
    return self.compute_check_digit(number) == int(number[-1])

def compute_numeric_code():
    return "".join([str(randint(0, 9)) for i in range(5)])


