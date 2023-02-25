# -*- encoding: utf-8 -*-

from random import randint

MOVE_DOCUMENT_TYPES = {
    'out_invoice': "01",
    'out_refund': "04",
    'in_invoice': "07", # Withholding
    'debit_note': "05",
    'waybill': '06',
}


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
    return str(cd)


def compute_numeric_code():
    return "".join([str(randint(0, 9)) for i in range(8)])


def compute_access_key(
        issuing_date,
        move_type,
        identifier,
        environment,
        l10n_latam_document_number):
    """Compute access key for electronic voucher"""

    ak = "{issuing_date}{voucher_type}{identifier}{environment}{sequence}{numeric_code}{issuing_type}".format(
        issuing_date=issuing_date.strftime("%d%m%Y"),
        voucher_type=MOVE_DOCUMENT_TYPES[move_type],
        identifier=identifier,
        environment=environment,
        sequence=l10n_latam_document_number.replace('-', ''),
        numeric_code=compute_numeric_code(),
        issuing_type="1",
    )

    ak = ak + compute_check_digit(ak)

    return ak
