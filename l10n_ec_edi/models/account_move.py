# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import base64
import json
from ecedi import accesskey
from odoo import _, api, fields, models
from odoo.tools.misc import formatLang, format_date, get_lang
from collections import defaultdict

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ec_move_access_key = fields.Char("Move Access Key")
    l10n_ec_withholding_access_key = fields.Char("Withholding Access Key")

    l10n_ec_move_numeric_code = fields.Char("Numeric Code", default="00000000")
    l10n_ec_withholding_numeric_code = fields.Char("Withholding Numeric Code", default="00000000")

    l10n_ec_edi_issuing_type = fields.Selection([
        ('1', 'Normal')],
        "Issuing Type",
        default='1',
    )

    l10n_ec_edi_environment_type = fields.Selection([
        ('1', 'Testing'),
        ('2', 'Production'),
        ], "Environment Type", default='1',
        compute="_compute_edi_environment",
        readonly=False
    )

    l10n_ec_edi_amount_by_group = fields.Binary(string="L10n EC Tax amount by group",
        compute='_l10n_ec_edi_compute_invoice_taxes_by_group',
        help='Edit Tax amounts if you encounter rounding issues.')

    l10n_ec_add_info_ids = fields.One2many(
        'ec.move.additional.info',
        'move_id',
        'Additional Info')

    @api.depends("name")
    def _compute_edi_environment(self):
        edi_environment_type = self.env['ir.config_parameter'].sudo().get_param("l10n_ec_edi.environment_type")
        for move in self:
            move.l10n_ec_edi_environment_type = edi_environment_type


    @api.depends('invoice_date', 'l10n_latam_document_number', 'l10n_ec_edi_environment_type', 'l10n_ec_edi_issuing_type', 'l10n_latam_document_type_id')
    def _compute_l10n_ec_move_ak(self):
        """Compute access key for electronic voucher"""

        for move in self:
            if not move.invoice_date or not move.l10n_latam_document_number \
                    or not move.company_id.vat \
                    or not move.l10n_latam_document_type_id \
                    or not move.l10n_ec_edi_issuing_type:
                move.l10n_ec_move_access_key = "0000000000000000000000000000000000000000000000000"
                move.l10n_ec_withholding_access_key = "0000000000000000000000000000000000000000000000000"
                continue

            ak = "{issuing_date}{voucher_type}{identifier}{environment}{sequence}{numeric_code}{issuing_type}".format(
                issuing_date=move.date.strftime("%d%m%Y"),
                voucher_type=move.l10n_latam_document_type_id.l10n_ec_edi_code,
                identifier=move.company_id.vat,
                environment=move.l10n_ec_edi_environment_type,
                sequence=move.l10n_latam_document_number.replace('-', ''),
                numeric_code=move.l10n_ec_withholding_numeric_code,
                issuing_type=move.l10n_ec_edi_issuing_type,
            )

            move.l10n_ec_move_access_key = "{}{}".format(ak, accesskey.calc_check_digit(ak))
            move.l10n_ec_withholding_access_key = "0000000000000000000000000000000000000000000000000"
    def invoice_generate_xml(self):
        self.ensure_one()
        report_name = "{}.xml".format(self.l10n_ec_move_access_key)
        description = _("Factura: %s", self.move_type)
        data = b"<?xml version='1.0' encoding='UTF-8'?>" +  self._export_invoice_as_xml()
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


    def _export_invoice_as_xml(self):
        template_values = self._prepare_export_edi_values()
        content = self.env.ref('l10n_ec_edi.factura')._render(template_values)
        return content




    def _prepare_export_edi_values(self):
        self.ensure_one()

        def get_partner_type(partner):
            if partner.vat == '9999999999999':
                return '07'
            elif partner.country_id.code != 'EC':
                return '08'
            else:
                return partner.l10n_latam_identification_type_id.l10n_ec_id_edi_code

        document_code = self.l10n_latam_document_type_id.l10n_ec_edi_code

        return {
            "record": self,
            "document_code": document_code,
            "partner_type": get_partner_type(self.partner_id),
            "environment": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.environment_type'),
            "issuing_type": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.issuing_type'),
        }

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_ec_taxes = fields.Binary(
        'Taxes',
        help='EDI taxes for account move line',
        compute='_l10n_ec_compute_taxes')

    @api.depends('tax_ids', 'tax_line_id')
    def _l10n_ec_compute_taxes(self):
        """Returns a list with tax computation as Ecuadorian SRI needs"""

        import pdb; pdb.set_trace();
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
    

