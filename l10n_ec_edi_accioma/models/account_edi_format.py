# Copyright 2021 Akretion (https://www.akretion.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import _, api, fields, models


_logger = logging.getLogger(__name__)

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    # --------------------------------------------------------------------------------                                                                                 
    # Export
    # --------------------------------------------------------------------------------

    l10n_latam_document_type_id = fields.Many2one(
        'l10n_latam.document.type',
        'Latam Document Type')

    xml_template_name = fields.Char("Template Name")

    def _is_compatible_with_journal(self, journal):
        _logger.info("IS COMPATIBLE WITH JOURNAL") 
        return journal.type == 'sale'

    def _is_required_for_invoice(self, invoice):
        return True

    #  def _post_factura(self, invoices):
    #      res = invoices.invoice_generate_xml()
    #
    #      return {invoices: res}


    def _post_invoice_edi(self, invoices, test_mode=False):
        """Overrides"""
        res = {}
        for inv in invoices:
            if inv.move_type == 'out_invoice':
                description = _("Factura: %s", inv.move_type)
                report_name = "{}.xml".format(inv.l10n_ec_move_access_key)
                data = inv.invoice_generate_xml()
                attachment = self.env['ir.attachment'].create({
                    'type': 'binary',
                    'name': report_name,
                    'raw': data,
                    'description': description,
                    #  'datas': base64.encodebytes(data),
                    'mimetype': 'application/xml',
                    'res_model': inv._name,
                    'res_id': inv.id,
                })
                res[inv] = {'attachment': attachment}

                inv.message_post(
                    body=(_("E-Invoice is generated on %s by %s") % (fields.Datetime.now(), self.env.user.display_name))
                )
        return res
    
