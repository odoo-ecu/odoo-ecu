# -*- encoding: utf-8 -*-
# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    l10n_ec_waybill_invoice_number = fields.Char("Invoice", compute="_get_invoice_name", readonly=True, copy=False)
    l10n_ec_waybill_invoice_auth = fields.Char("Invoice Authorization", compute="_get_invoice_name", readonly=True, copy=False)
    l10n_ec_waybill_invoice_date = fields.Date("Invoice Date", compute="_get_invoice_name", readonly=True, copy=False)
    l10n_ec_waybill_document_number = fields.Char("Document Number")
    l10n_ec_waybill_last_sequence = fields.Char("Waybill Last Sequence", compute="_compute_l10n_ec_waybill_l_seq")
    l10n_ec_waybill_id = fields.Many2one(
        'ec.waybill',
        'L10N Ec Waybill')
    
    l10n_ec_waybill_warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Waybill Warehouse')
    
    is_l10n_ec_waybill = fields.Boolean("Waybill?")
    l10n_ec_waybill_before = fields.Boolean("Waybill before", default=False)
    
    l10n_ec_waybill_access_key = fields.Char("Access Key", readonly=True, copy=False)

    transport_start_date = fields.Date("Transport Start Date")
    transport_end_date = fields.Date("Transport End Date")
    vehicle_id =  fields.Many2one('fleet.vehicle', 'Transport Vehicle')
    driver_id = fields.Many2one('res.partner', 'Vehicle Driver')
    l10n_ec_waybill_partner_vat = fields.Char("Waybill Partner VAT", compute="_get_invoice_name")
    l10n_ec_waybill_partner_name = fields.Char("Waybill Partner Name", compute="_get_invoice_name")
    l10n_ec_waybill_partner_street = fields.Char("Waybill Partner Street", compute="_get_invoice_name")

    @api.depends("partner_id", "location_dest_id")
    def _get_waybill_partner_data(self):
        """Get partner data for waybill either it is sale or internal transfer"""
        for picking in self:
            if picking.partner_id:
                picking.l10n_ec_waybill_partner_vat = picking.partner_id.vat
                picking.l10n_ec_waybill_partner_name = picking.partner_id.name
                picking.l10n_ec_waybill_partner_street = picking.partner_id.street
            
            else:
                picking.l10n_ec_waybill_partner_vat = picking.company_id.vat
                picking.l10n_ec_waybill_partner_name = picking.company_id.name
                picking.l10n_ec_waybill_partner_street = picking.location_dest_id.get_warehouse().partner_id.street


    @api.depends('sale_id')
    def _get_invoice_name(self):
        for picking in self:
            if picking.sale_id:
                picking.l10n_ec_waybill_partner_vat = picking.sale_id.partner_id.vat
                picking.l10n_ec_waybill_partner_name = picking.sale_id.partner_id.name
                picking.l10n_ec_waybill_partner_street = picking.sale_id

                invoices = picking.sale_id.invoice_ids
                if invoices:
                    picking.l10n_ec_waybill_invoice_number = \
                            invoices[0].l10n_latam_document_number or \
                            invoices[0].l10n_latam_manual_document_number
                    picking.l10n_ec_waybill_invoice_auth = \
                            invoices[0].l10n_ec_move_access_key
                    picking.l10n_ec_waybill_invoice_date = \
                            invoices[0].invoice_date

                else:
                    picking.l10n_ec_waybill_invoice_number = ""
                    picking.l10n_ec_waybill_partner_vat = picking.company_id.vat
                    picking.l10n_ec_waybill_partner_name = picking.company_id.name
                    picking.l10n_ec_waybill_partner_street = picking.company_id.street
                    picking.l10n_ec_waybill_invoice_auth = ""


            else:
                picking.l10n_ec_waybill_invoice_number = ""
                picking.l10n_ec_waybill_partner_vat = picking.company_id.vat
                picking.l10n_ec_waybill_partner_name = picking.company_id.name
                picking.l10n_ec_waybill_partner_street = picking.company_id.street
                picking.l10n_ec_waybill_invoice_auth = ""

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.driver_id = self.vehicle_id.driver_id
        else:
            self.driver_id = None

    @api.constrains('l10n_ec_waybill_document_number')
    def _check_waybill_document_number(self):
        doc_num_format = "^\d{3}-\d{3}-\d{9}$"
        for waybill in self.filtered(lambda waybill: waybill.is_l10n_ec_waybill == True):
            if not waybill.l10n_ec_waybill_document_number:
                continue
            if not re.match(doc_num_format, waybill.l10n_ec_waybill_document_number):
                raise ValidationError(_("Document number format invalid {}".format(waybill.l10n_ec_waybill_document_number)))


    @api.depends('is_l10n_ec_waybill')
    def _compute_l10n_ec_waybill_l_seq(self):

        self.ensure_one()
        sql = """
              SELECT MAX(l10n_ec_waybill_document_number) 
              FROM stock_picking WHERE l10n_ec_waybill_warehouse_id = %(warehouse_id)s 
              """

        self.env.cr.execute(sql, {'warehouse_id': self.l10n_ec_waybill_warehouse_id.id or -1 }) 
        seq = (self.env.cr.fetchone() or [None])[0]
        self.l10n_ec_waybill_last_sequence = seq or "/"

    def action_waybill(self):
        for picking in self:
            warehouse_id = picking.location_id.get_warehouse()
            picking.l10n_ec_waybill_warehouse_id = warehouse_id
            _logger.info(f"Warehouse {warehouse_id}")
            picking.l10n_ec_waybill_warehouse_id = warehouse_id
            picking.is_l10n_ec_waybill = not picking.is_l10n_ec_waybill

    def _assign_l10n_ec_waybill_document_number(self):
        """Assign waybill document number, to be used after validation"""

        for waybill in self.filtered(lambda waybill: waybill.is_l10n_ec_waybill == True):
            self._compute_l10n_ec_waybill_l_seq()
            if waybill.l10n_ec_waybill_last_sequence != "/" and not waybill.l10n_ec_waybill_before:
                seq_val = waybill.l10n_ec_waybill_last_sequence.split("-")
                sequence = int(seq_val[-1]) + 1
                seq_val[-1] = "{:09}".format(sequence) 
                waybill.l10n_ec_waybill_document_number = "-".join(seq_val)
                waybill.l10n_ec_waybill_before = True

    def _prepare_export_edi_values(self):
        self.ensure_one()

        def get_partner_type(partner):
            if partner.vat == '9999999999999':
                return '07'
            elif partner.country_id.code != 'EC':
                return '08'
            else:
                return partner.l10n_latam_identification_type_id.l10n_ec_id_edi_code

        return {
            "record": self,
            "partner_type": get_partner_type(self.partner_id),
            "environment": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.environment_type'),
            "issuing_type": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.issuing_type'),
        }


    #  def waybill_generate_xml(self):
    #      self.ensure_one()
    #      report_name = "{}.xml".format(self.l10n_ec_waybill_document_number)
    #      description = _("Guia Remision: %s", self.move_type)
    #      data = b"<?xml version='1.0' encoding='UTF-8'?>" +  self._export_waybill_as_xml()
    #      return data
    #
    #  def _export_waybill_as_xml(self):
    #      template_values = self._prepare_export_edi_values()
    #      content = self.env.ref('l10n_ec_waybill.guia_remision')._render(template_values)
    #      return content
    #





    

