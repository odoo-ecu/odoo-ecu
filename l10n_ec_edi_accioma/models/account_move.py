# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from random import randint
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from collections import defaultdict

_logger = logging.getLogger(__name__)

MOVE_DOCUMENT_TYPES = {
    'out_invoice': "01",
    'out_refund': "04",
    'in_invoice': "07",
    'debit_note': "05",
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ec_edi_not_compatible = fields.Boolean('EC EDI not compatible')

    l10n_ec_edi_amount_by_group = fields.Binary(string="L10n EC Tax amount by group",
        compute='_l10n_ec_edi_compute_invoice_taxes_by_group',
        help='Edit Tax amounts if you encounter rounding issues.')

    l10n_ec_add_info_ids = fields.One2many(
        'ec.move.additional.info',
        'move_id',
        'Additional Info')

    def _validate_edi_config(self):
        for move in self:
            pass

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
        return str(cd)

    @api.model
    def is_valid(self, number):
        if not all([d.isdigit() for d in number]):
            return False
        return self.compute_check_digit(number) == int(number[-1])

    @api.model
    def compute_numeric_code(self):
        return "".join([str(randint(0, 9)) for i in range(8)])

    def _compute_l10n_ec_move_ak(self):
        """Compute access key for electronic voucher"""

        res = []
        for move in self:
            if not move.invoice_date or not move.l10n_latam_document_number \
                    or not move.company_id.vat \
                    or not move.l10n_latam_document_type_id:

                m = []
                if not move.l10n_latam_document_number:
                    m.append(_("Latam Document Number not found"))

                if not move.company_id.vat:
                    m.append(_("VAT not found"))

                if not move.l10n_latam_document_type_id:
                    m.append(_("Latam Document Type not found"))

                res.append((move.id, False, ", ".join(m)))
                continue

            edi_env = self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi_accioma.environment_type')

            if not edi_env:
                raise UserError(_("Please configure environment type before issue electronic documents"))

            environment = [x for x in edi_env][0] or "1"
            numeric_code = self.env['l10nec.edi.document'].sudo().compute_numeric_code()

            ak = "{issuing_date}{voucher_type}{identifier}{environment}{sequence}{numeric_code}{issuing_type}".format(
                issuing_date=move.date.strftime("%d%m%Y"),
                voucher_type=MOVE_DOCUMENT_TYPES[move.move_type],
                identifier=move.company_id.vat,
                environment=environment,
                sequence=move.l10n_latam_document_number.replace('-', ''),
                numeric_code=numeric_code,
                issuing_type="1",
            )
            _logger.info(ak)
            ak = ak + self.compute_check_digit(ak)
            res.append((move.id, ak))

        return res

    def _post(self, soft=True):
        # OVERRIDE
        # Set the electronic document to be posted and post immediately for synchronous formats.
        posted = super()._post(soft=soft)

        if self.journal_id.company_id.account_fiscal_country_id.code != 'EC' or \
                not self.journal_id.l10n_latam_use_documents:
            return posted

        aks = self._compute_l10n_ec_move_ak()

        for ak in aks:
            this = self.browse(ak[0])
            if self.type == 'out_invoice':
                xml_content = "<?xml version='1.0' encoding='UTF-8'?>" + str(this._l10n_ec_export_invoice_as_xml(ak))
            else:
                continue

            edi_values = {
                'state': 'to_send',
                'name': ak[1],
                'xml_content': xml_content,
                'model': 'account.move',
                'res_id': ak[0],
                'company_id': this.company_id.id,
                'ecu_document_type': MOVE_DOCUMENT_TYPES[self.move_type],
            }

            document_id = self.env['l10nec.edi.document'].create(edi_values)

        return posted

    def invoice_generate_xml(self):
        self.ensure_one()
        report_name = "{}.xml".format(self.l10n_ec_move_access_key)
        description = _("Factura: %s", self.move_type)
        data = b"<?xml version='1.0' encoding='UTF-8'?>" + self._export_invoice_as_xml()
        return data

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id')
    def _l10n_ec_edi_compute_invoice_taxes_by_group(self):
        for move in self:

            # Not working on something else than invoices.
            if not move.is_invoice(include_receipts=True):
                move.l10n_ec_edi_amount_by_group = []
                continue

            lang_env = move.with_context(lang=move.partner_id.lang).env
            balance_multiplicator = -1 if move.is_inbound() else 1

            tax_lines = move.line_ids.filtered('tax_line_id')
            base_lines = move.line_ids.filtered('tax_ids')

            tax_group_mapping = defaultdict(lambda: {
                'base_lines': set(),
                'base_amount': 0.0,
                'tax_amount': 0.0,
            })

            # Compute base amounts.
            for base_line in base_lines:
                base_amount = balance_multiplicator * (base_line.amount_currency if base_line.currency_id else base_line.balance)

                for tax in base_line.tax_ids.flatten_taxes_hierarchy():

                    if base_line.tax_line_id.tax_group_id == tax.tax_group_id:
                        continue

                    tax_group_vals = tax_group_mapping[tax.tax_group_id]
                    if base_line not in tax_group_vals['base_lines']:
                        tax_group_vals['base_amount'] += base_amount
                        tax_group_vals['base_lines'].add(base_line)

            # Compute tax amounts.
            for tax_line in tax_lines:
                tax_amount = balance_multiplicator * (tax_line.amount_currency if tax_line.currency_id else tax_line.balance)
                tax_group_vals = tax_group_mapping[tax_line.tax_line_id.tax_group_id]
                tax_group_vals['tax_amount'] += tax_amount

            tax_groups = sorted(tax_group_mapping.keys(), key=lambda x: x.sequence)
            amount_by_group = []
            for tax_group in tax_groups:
                tax_group_vals = tax_group_mapping[tax_group]
                amount_by_group.append((
                    tax_group.l10n_ec_edi_group_code,
                    tax_group.l10n_ec_edi_percentage_code,
                    tax_group_vals['base_amount'],
                    tax_group_vals['tax_amount'],
                ))
            move.l10n_ec_edi_amount_by_group = amount_by_group

    def _l10n_ec_export_invoice_as_xml(self, ak):
        template_values = self._prepare_export_edi_values(ak)
        content = self.env['ir.qweb']._render('l10n_ec_edi_accioma.factura', template_values)
        return content


    def _l10n_ec_get_payment_data(self):
        """ Get payment data for the XML.  """
        payment_data = []
        pay_term_line_ids = self.line_ids.filtered(
            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable')
        )
        for line in pay_term_line_ids:
            payment_vals = {
                'payment_code': self.l10n_ec_sri_payment_id.code or '20',
                'payment_total': abs(line.balance),
            }
            if self.invoice_payment_term_id and line.date_maturity:
                payment_vals.update({
                    'payment_term': max(((line.date_maturity - self.invoice_date).days), 0),
                    'time_unit': "dias",
                })
            payment_data.append(payment_vals)
        return payment_data

    def _prepare_export_edi_values(self, ak):
        self.ensure_one()

        def get_partner_type(partner):
            if partner.vat == '9999999999999':
                return '07'
            elif partner.country_id.code != 'EC':
                return '08'
            else:
                return partner.l10n_latam_identification_type_id.l10n_ec_id_edi_code

        document_code = self.l10n_latam_document_type_id.l10n_ec_edi_code

        payment_data = self._l10n_ec_get_payment_data()
        _logger.info(f"Payment data {payment_data}")
        return {
            "record": self,
            "access_key": ak[1],
            "document_code": document_code,
            "partner_type": get_partner_type(self.partner_id),
            "environment": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi_accioma.environment_type'),
            "issuing_type": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi_accioma.issuing_type'),
            "payment_data": self._l10n_ec_get_payment_data(),
        }

    def action_view_edi_documents(self):
        action = self.env["ir.actions.actions"]._for_xml_id("l10n_ec_edi_accioma.l10n_ec_edi_document")
        action['domain'] = [('res_id', '=', self.id), ('model', '=', 'account.move')]
        return action


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_ec_taxes = fields.Binary(
        'Taxes',
        help='EDI taxes for account move line',
        compute='_l10n_ec_compute_taxes')

    @api.depends('tax_ids', 'tax_line_id')
    def _l10n_ec_compute_taxes(self):
        """Returns a list with tax computation as Ecuadorian SRI needs"""

        for line in self:
            taxes = []
            base_imponible = abs(line.amount_currency if line.amount_currency else line.balance)
            for tax in self.tax_ids:
                taxes.append({
                    'codigo': tax.tax_group_id.l10n_ec_edi_group_code,
                    'codigo_porcentaje': tax.tax_group_id.l10n_ec_edi_percentage_code,
                    'tarifa': tax.tax_group_id.l10n_ec_edi_percentage,
                    'base_imponible': base_imponible,
                    'valor': base_imponible * tax.tax_group_id.l10n_ec_edi_percentage / 100,
                })

            line.l10n_ec_taxes = taxes


class EcMoveAdditionalInfo(models.Model):
    _name = 'ec.move.additional.info'
    _description = 'Ec Move Additional Info'

    move_id = fields.Many2one(
        'account.move',
        'Move')
    key = fields.Char("Key")
    value = fields.Char("Value")


