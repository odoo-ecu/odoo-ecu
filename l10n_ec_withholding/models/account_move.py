# Copyright 2021 Akretion (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging, ecedi, json
from collections import defaultdict
from functools import reduce
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ec_withholding_type = fields.Selection([
        ('in_withholding', 'Customer Withholding'),
        ('out_withholding', 'Vendor Withholding'),
        ('no_withholding', 'There is no Withholding'),
        ], "withholding Type",  compute='_compute_withholding_type'
        )

    l10n_ec_withholding_number = fields.Char("Withholding Number")
    l10n_ec_highest_withholding_number = fields.Char("Highgest Withholding Number", compute="_get_highest_withholding_number")
    l10n_ec_withholding_data = fields.Binary("Withholding", compute="_l10n_ec_compute_withholding_data")
    #  l10n_ec_withholding_data_txt = fields.Text("Withholding Data Text", compute="_l10n_ec_compute_withholding_data")


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

        for move in self:
            if move.posted_before:
                continue
            group = grouped[journal_key(move)][date_key(move)]
            if not group['records']:
                # Compute all the values needed to sequence this whole group
                last_sequence = self[0]._get_last_withholding_sequence()
                if move.l10n_ec_withholding_type == "out_withholding":
                    self.l10n_ec_withholding_number = ecedi.sequence.next_sequence(last_sequence)

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

            #  move.l10n_ec_withholding_data_txt = json.dumps(withholding_taxes)
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





    

