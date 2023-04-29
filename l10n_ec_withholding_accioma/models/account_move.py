# Copyright 2021 Akretion (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging, json
from collections import defaultdict
from functools import reduce
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

L10N_EC_TAXES_SUPPORT = [
    ('01', '01 Tax credit for VAT declaration (services and goods other than inventories and fixed assets)'),
    ('02', '02 Cost or Expense for IR declaration (services and goods other than inventories and fixed assets)'),
    ('03', '03 Fixed Asset - Tax Credit for VAT return'),
    ('04', '04 Fixed Asset - Cost or Expense for IR declaration'),
    ('05', '05 Settlement of travel, lodging and food expenses IR expenses (on behalf of employees and not of the company)'),
    ('06', '06 Inventory - Tax Credit for VAT return'),
    ('07', '07 Inventory - Cost or Expense for IR declaration'),
    ('08', '08 Amount paid to request Expense Reimbursement (intermediary)'),
    ('09', '09 Claims Reimbursement'),
    ('10', '10 Distribution of Dividends, Benefits or Profits'),
    ('15', '15 Payments made for own and third-party consumption of digital services'),
    ('00', '00 Special cases whose support does not apply to the above options')
]

L10N_EC_TAXES_SUPPORT_LATAM_DOCUMENT_MAPPING = [
    ('01', ('01', '02', '03', '04', '05', '06', '07', '08', '09', '14', '15', '00')),
    ('02', ('02', '04', '05', '07', '08', '14', '15', '00')),
    ('03', ('01', '02', '03', '04', '05', '06', '07', '08', '14', '15')),
    ('04', ('01', '02', '03', '04', '05', '06', '07', '08', '09', '14', '15', '00')),

]

L10N_EC_VAT_RATES = {
    2: 12.0,
    3: 14.0,
    0: 0.0,
    6: 0.0,
    7: 0.0,
    8: 8.0,
}
L10N_EC_VAT_SUBTAXES = {
    'vat08': 8,
    'vat12': 2,
    'vat14': 3,
    'zero_vat': 0,
    'not_charged_vat': 6,
    'exempt_vat': 7,
}  # NOTE: non-IVA cases such as ICE and IRBPNR not supported
L10N_EC_VAT_TAX_NOT_ZERO_GROUPS = (
    'vat08',
    'vat12',
    'vat14',
)
L10N_EC_VAT_TAX_ZERO_GROUPS = (
    'zero_vat',
    'not_charged_vat',
    'exempt_vat',
)
L10N_EC_VAT_TAX_GROUPS = tuple(L10N_EC_VAT_TAX_NOT_ZERO_GROUPS + L10N_EC_VAT_TAX_ZERO_GROUPS)  # all VAT taxes
L10N_EC_WITHHOLD_CODES = {
    'withhold_vat_purchase': 2,
    'withhold_income_purchase': 1,
}
L10N_EC_WITHHOLD_VAT_CODES = {
    0.0: 7,  # 0% vat withhold
    10.0: 9,  # 10% vat withhold
    20.0: 10,  # 20% vat withhold
    30.0: 1,  # 30% vat withhold
    50.0: 11, # 50% vat withhold
    70.0: 2,  # 70% vat withhold
    100.0: 3,  # 100% vat withhold
}  # NOTE: non-IVA cases such as ICE and IRBPNR not supported
# Codes from tax report "Form 103", useful for withhold automation:
L10N_EC_WTH_FOREIGN_GENERAL_REGIME_CODES = ['402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413', '414', '415', '416', '417', '418', '419', '420', '421', '422', '423']
L10N_EC_WTH_FOREIGN_TAX_HAVEN_OR_LOWER_TAX_CODES = ['424', '425', '426', '427', '428', '429', '430', '431', '432', '433']
L10N_EC_WTH_FOREIGN_NOT_SUBJECT_WITHHOLD_CODES = ['412', '423', '433']
L10N_EC_WTH_FOREIGN_SUBJECT_WITHHOLD_CODES = list(set(L10N_EC_WTH_FOREIGN_GENERAL_REGIME_CODES) - set(L10N_EC_WTH_FOREIGN_NOT_SUBJECT_WITHHOLD_CODES))
L10N_EC_WTH_FOREIGN_DOUBLE_TAXATION_CODES = ['402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412']
L10N_EC_WITHHOLD_FOREIGN_REGIME = [('01', '(01) General Regime'), ('02', '(02) Fiscal Paradise'), ('03', '(03) Preferential Tax Regime')]


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ec_withholding_support = fields.Selection(selection=[
    ('01', '01 Tax credit for VAT declaration (services and goods other than inventories and fixed assets)'),
    ('02', '02 Cost or Expense for IR declaration (services and goods other than inventories and fixed assets)'),
    ('03', '03 Fixed Asset - Tax Credit for VAT return'),
    ('04', '04 Fixed Asset - Cost or Expense for IR declaration'),
    ('05', '05 Settlement of travel, lodging and food expenses IR expenses (on behalf of employees and not of the company)'),
    ('06', '06 Inventory - Tax Credit for VAT return'),
    ('07', '07 Inventory - Cost or Expense for IR declaration'),
    ('08', '08 Amount paid to request Expense Reimbursement (intermediary)'),
    ('09', '09 Claims Reimbursement'),
    ('10', '10 Distribution of Dividends, Benefits or Profits'),
    ('15', '15 Payments made for own and third-party consumption of digital services'),
    ('00', '00 Special cases whose support does not apply to the above options')
]
, string="Withholding Support")

    l10n_ec_withholding_type = fields.Selection([
        ('in_withholding', 'Customer Withholding'),
        ('out_withholding', 'Vendor Withholding'),
        ('no_withholding', 'There is no Withholding'),
        ], "withholding Type",  compute='_compute_withholding_type'
        )

    l10n_ec_withholding_number = fields.Char("Withholding Number")
    l10n_ec_highest_withholding_number = fields.Char("Highgest Withholding Number", compute="_get_highest_withholding_number")
    l10n_ec_withholding_data = fields.Binary("Withholding", compute="_l10n_ec_compute_withholding_data")
    l10n_ec_withholding_data_txt = fields.Text("Withholding Data Text", compute="_l10n_ec_compute_withholding_data")
    description = fields.Text("Description")

    @api.depends("move_type", "line_ids")
    def _compute_withholding_type(self):
        """Determine the type of withholding which is necesary for withholding
        number calculation"""
        for rec in self:
            withholding_taxes = []
            if rec.move_type == "in_invoice":
                base_lines = rec.line_ids.filtered('tax_ids')
                for base_line in base_lines:
                    for tax in base_line.tax_ids.flatten_taxes_hierarchy().filtered(
                            lambda x: x.tax_group_id.l10n_ec_type in (
                                'withhold_vat', 'withhold_income_tax')):
                        withholding_taxes.append(tax)
                if withholding_taxes:
                    rec.l10n_ec_withholding_type = "out_withholding"
                else:
                    rec.l10n_ec_withholding_type = "no_withholding"


            elif rec.move_type == "out_invoice":
                rec.l10n_ec_withholding_type = "in_withholding"
            else:
                rec.l10n_ec_withholding_type = "no_withholding"

    def _get_last_withholding_sequence(self):
        """Withholding sequence by journal, as journal is the equivalent of
        issueing point"""
        self.ensure_one()

        param = {}
        param['journal_id'] = self.journal_id.id

        query = """
            SELECT MAX(l10n_ec_withholding_number)
            FROM account_move
            WHERE journal_id = %(journal_id)s

        """

        self.env.cr.execute(query, param)
        return (self.env.cr.fetchone() or [None])[0]

    @api.depends("journal_id")
    def _get_highest_withholding_number(self):
        """Highest withholdig sequence number"""
        for record in self:
            record.l10n_ec_highest_withholding_number= record._get_last_withholding_sequence()

    @api.depends('posted_before', 'state', 'journal_id', 'date', 'l10n_ec_withholding_type')
    def _compute_name(self):

        def journal_key(move):
            return (move.journal_id, move.journal_id.refund_sequence and move.move_type)

        def date_key(move):
            return (move.date.year, move.date.month)

        grouped = defaultdict(  # key: journal_id, move_type
            lambda: defaultdict(  # key: first adjacent (date.year, date.month)
                lambda: {
                    'records': self.env['account.move'],
                    'format': False,
                    'format_values': False,
                    'reset': False
                }
            )
        )

        self = self.sorted(lambda m: (m.date, m.ref or '', m.id))

        # for move in self:
        #     if move.posted_before:
        #         continue
        #     group = grouped[journal_key(move)][date_key(move)]
        #     if not group['records']:
        #         # Compute all the values needed to sequence this whole group
        #         last_sequence = self[0]._get_last_withholding_sequence()
        #         if move.l10n_ec_withholding_type == "out_withholding":
        #             self.l10n_ec_withholding_number = ecedi.sequence.next_sequence(last_sequence)

        super(AccountMove, self)._compute_name()

    def _l10n_ec_compute_base_line_vat_amount(self, line):
        """Compute line vat amount"""
        vat_taxes = [tax for tax in line if tax['type'][0:3] == 'vat']
        new_line = [tax for tax in line if tax['type'][0:3] != 'vat']

        if not vat_taxes:
            new_line.append(0.0)
            return new_line

        new_line.append(
            reduce(
                lambda x, y: x+y,
                    map(lambda t:
                        t['base_imponible'] * t['porcentaje'] / 100, vat_taxes)) or 0.0)
        return new_line

    def _l10n_ec_compute_withhold_tax_amount(self, line):
        line = self._l10n_ec_compute_base_line_vat_amount(line)
        vat_amount = line.pop()

        for tax in line:
            if tax['type'] == 'withhold_vat':
                tax['base_imponible'] = vat_amount
            else:
                tax['porcentaje_retener'] = -1 * tax['porcentaje']

            tax['valor_retenido'] = tax['base_imponible'] * tax['porcentaje_retener'] / 100

        return line


    @api.depends("move_type", "line_ids")
    def _l10n_ec_compute_withholding_data(self):
        """Compute withholding data"""
        for move in self:
            base_lines = move.line_ids.filtered('tax_ids')
            tax_lines = move.line_ids.filtered('tax_line_id')

            tax_group_mapping = defaultdict(lambda: {
                #  'base_lines': set(),
                'base_amount': 0.0,
                'tax_amount': 0.0,
                'amount_type': "",
            })

            taxes = []
            # Compute base amount
            for base_line in base_lines:
                base_line_taxes = []
                base_imponible = abs(base_line.amount_currency if base_line.amount_currency else base_line.balance)
                _logger.info(f"Base Imponible {base_imponible}")
                for tax in base_line.tax_ids:
                    #  if tax.tax_group_id.l10n_ec_type in (
                    #          'withhold_vat', 'withhold_income_tax'):

                        #  taxes.append({
                    if tax.amount_type == 'group':
                        for gtax in tax.children_tax_ids:

                            base_line_taxes.append({
                                'id': gtax.id,
                                'type': gtax.tax_group_id.l10n_ec_type,
                                'porcentaje': gtax.amount,
                                'porcentaje_retener': gtax.withhold_amount,
                                'valor_retenido': 0.0,
                                'base_imponible': base_imponible,
                                'codigo': gtax.tax_group_id.l10n_ec_edi_percentage_code,
                                'name': gtax.name,
                                'codigo_retencion': gtax.l10n_ec_code_ats,
                            })

                    else:

                        base_line_taxes.append({
                            'id': tax.id,
                            'type': tax.tax_group_id.l10n_ec_type,
                            'porcentaje': tax.amount,
                            'porcentaje_retener': tax.withhold_amount,
                            'valor_retenido': 0.0,
                            'base_imponible': base_imponible,
                            'codigo': tax.tax_group_id.l10n_ec_edi_percentage_code,
                            'name': tax.name,
                            'codigo_retencion': tax.l10n_ec_code_ats,
                        })

                taxes.append(self._l10n_ec_compute_withhold_tax_amount(base_line_taxes))

            withholding_taxes_group = defaultdict(list)

            _logger.info("Withholding Taxes : {}".format(taxes))
            for tax in taxes:
                for t in tax:
                    if t['type'] in (
                                'withhold_vat', 'withhold_income_tax') \
                            and t['base_imponible'] > 0:
                        withholding_taxes_group[t['id']].append(t)

            _logger.info("Withholding Taxes Group : {}".format(withholding_taxes_group))
            for k in withholding_taxes_group:
                while len(withholding_taxes_group[k]) > 1:
                    tax = withholding_taxes_group[k].pop()
                    _logger.info("Tax {}".format(tax))
                    withholding_taxes_group[k][0]['base_imponible'] += tax['base_imponible']
                    withholding_taxes_group[k][0]['valor_retenido'] += tax['valor_retenido']

            withholding_taxes = []
            for k, v in withholding_taxes_group.items():
                withholding_taxes.append(v[0])

            move.l10n_ec_withholding_data_txt = json.dumps(withholding_taxes)
            move.l10n_ec_withholding_data = withholding_taxes
            _logger.info("Winholding Data: {}".format(withholding_taxes))

    l10n_ec_withholding_taxes = fields.Binary(
        'Taxes',
        help='EDI taxes for account move line',
        compute='_l10n_ec_compute_taxes')

    @api.depends('tax_ids', 'tax_line_id')
    def _l10n_ec_compute_withholding_taxes(self):
        """Returns a list with tax computation as Ecuadorian SRI needs"""

        for line in self:
            taxes = []
            base_imponible = abs(self.amount_currency if self.amount_currency else self.balance)
            import pdb; pdb.set_trace();
            for tax in self.tax_ids:
                taxes.append({
                    'codigo': tax.tax_group_id.l10n_ec_edi_group_code,
                    'codigo_porcentaje': tax.tax_group_id.l10n_ec_edi_percentage_code,
                    'tarifa': tax.tax_group_id.l10n_ec_edi_percentage,
                    'base_imponible': base_imponible,
                    'valor': base_imponible * tax.tax_group_id.l10n_ec_edi_percentage / 100,
                })

            line.l10n_ec_withholding_taxes = taxes

    def _export_withhold_as_xml(self):
        template_values = self._prepare_export_withhold_edi_values()
        content = self.env.ref('l10n_ec_withholding.retencion')._render(template_values)
        return content

    def _prepare_export_withhold_edi_values(self):
        self.ensure_one()

        def get_partner_type(partner):
            if partner.vat == '9999999999999':
                return '07'
            elif partner.country_id.code != 'EC':
                return '08'
            else:
                return partner.l10n_latam_identification_type_id.l10n_ec_id_edi_code

        _logger.info("Periodo fiscal {}".format(self.date.strftime('%m/%Y')))
        return {
            "record": self,
            "periodo_fiscal": "{}".format(self.date.strftime('%m/%Y')),
            "partner_type": get_partner_type(self.partner_id),
            "environment": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.environment_type'),
            "issuing_type": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.issuing_type'),
            "withholding_data": self.l10n_ec_withholding_data,
        }

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('tax_ids')
    def _check_vat_retention(self):
        for line in self:
            # Check for vat retention tax
            if any(
                [tax.tax_group_id.l10n_ec_type == 'withhold_vat' for tax in line.tax_ids]) and \
                not any(
                    [tax.tax_group_id.l10n_ec_type[0:3] == 'vat' for tax in line.tax_ids]):

                raise models.ValidationError(_("Please insert a VAT tax before a VAT retention tax"))







