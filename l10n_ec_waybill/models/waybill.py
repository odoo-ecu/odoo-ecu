# -*- encoding: utf-8 -*-
# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime,date,timedelta
from odoo.addons.l10n_ec_edi.tools import formats

_logger = logging.getLogger(__name__)

DOC_NUM_FORMAT = "^\d{3}-\d{3}-\d{9}$"

class EcWaybill(models.Model):
    _name = 'ec.waybill'
    _description = 'Ecuador Waybill'


    name =  fields.Char('Number', default="GR Borrador")
    l10n_ec_waybill_document_number = fields.Char("Document Number", copy=False)
    l10n_ec_waybill_last_sequence = fields.Char("Waybill Last Sequence", compute="_compute_l10n_ec_waybill_l_seq")
    l10n_ec_waybill_before = fields.Boolean("Waybill before", default=False, copy=False)
    date = fields.Datetime('Transport Date',default = datetime.now(), copy=False, required=True)
    date_due = fields.Datetime('Transport Due Date',default = datetime.now(), copy=False, required=True)
    note = fields.Text('Note', copy=False)
    active = fields.Boolean('Active', default=True)
    picking_ids = fields.One2many(
        'ec.waybill.picking',
        'l10n_ec_waybill_id',
        'Delivery Orders')
    #  customer_id = fields.Many2one('res.partner', 'Customer')
    #  contact_person = fields.Char('Contact Name')
    #  no_of_parcels = fields.Integer('No Of Parcels')
    vehicle_id =  fields.Many2one('fleet.vehicle', 'Transport Vehicle', required=True)
    #  sale_order = fields.Char(string='Sale Order')
    #  tag_ids = fields.Many2one('fleet.vehicle', copy=False, string='Transport Vehicle')
    driver_id = fields.Many2one('res.partner', 'Vehicle Driver', required=True)
    state =  fields.Selection([
        ('draft', 'Start'),
        ('waiting','Waiting'),
        ('in-progress', 'In-Progress'),
        ('done','Done'),
        ('cancel','Cancel'),
        ],
        default =  'draft',
        copy = False)
    #  transport_id = fields.Many2one('transport', 'Transporter Name')
    #  transport_rote_ids  = fields.One2many('transport.location.details', 'transport_entry_id')
    user_id = fields.Many2one('res.users', string='Responsible User', index=True, default=lambda self: self.env.user)
    #  user_id = fields.Many2one('res.users', string='Responsible User', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
    location_id = fields.Many2one('stock.location', string='Source Location', domain=[('usage', '=', 'internal')], required=True)
    l10n_ec_waybill_warehouse_id = fields.Many2one(
        'stock.warehouse',
        'Waybill Warehouse')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.company)
    note = fields.Text('Note')
    l10n_ec_add_info_ids = fields.One2many(
        'ec.waybill.additional.info',
        'waybill_id',
        'Additional Info')

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.driver_id = self.vehicle_id.driver_id
        else:
            self.driver_id = None

    @api.constrains('l10n_ec_waybill_document_number')
    def _check_waybill_document_number(self):
        for waybill in self:
            if not waybill.l10n_ec_waybill_document_number:
                continue
            if not re.match(DOC_NUM_FORMAT, waybill.l10n_ec_waybill_document_number):
                raise ValidationError(_("Document number format invalid {}".format(waybill.l10n_ec_waybill_document_number)))

    @api.depends('location_id')
    def _compute_l10n_ec_waybill_l_seq(self):

        self.ensure_one()
        sql = """
              SELECT MAX(l10n_ec_waybill_document_number)
              FROM ec_waybill WHERE l10n_ec_waybill_warehouse_id = %(warehouse_id)s
              """

        self.env.cr.execute(sql, {'warehouse_id': self.location_id.warehouse_id.id or -1})
        seq = (self.env.cr.fetchone() or [None])[0]
        self.l10n_ec_waybill_last_sequence = seq or "/"

    @api.depends('location_id')
    def set_waybill_warehouse(self):
        for waybill in self:
            waybill.l10n_ec_waybill_warehouse_id = waybill.location_id.warehouse_id

    def _assign_l10n_ec_waybill_document_number(self):
        """Assign waybill document number, to be used after validation"""

        for waybill in self:
            self._compute_l10n_ec_waybill_l_seq()
            if waybill.l10n_ec_waybill_last_sequence != "/" and not waybill.l10n_ec_waybill_before:
                seq_val = waybill.l10n_ec_waybill_last_sequence.split("-")
                sequence = int(seq_val[-1]) + 1
                seq_val[-1] = "{:09}".format(sequence)
                waybill.l10n_ec_waybill_document_number = "-".join(seq_val)
                waybill.l10n_ec_waybill_before = True

    def _compute_l10n_ec_waybill_ak(self):
        """Compute access key for electronic voucher"""
        self.ensure_one()

        issuing_date = self.date
        voucher_type = 'waybill' # Waybill
        identifier = self.company_id.vat
        environment = self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.environment_type')
        document_number = self.l10n_ec_waybill_document_number

        return formats.compute_access_key(
            issuing_date,
            voucher_type,
            identifier,
            environment,
            document_number
        )

    def action_validate(self):
        """Overrides action done so it adds the waybill number assignment
        functionality"""

        for waybill in self:
            if waybill.l10n_ec_waybill_last_sequence == "/" and \
                    not re.match(DOC_NUM_FORMAT, waybill.l10n_ec_waybill_document_number):
                raise ValidationError(_("Please setup a new sequence"))

            if not waybill.picking_ids:
                raise ValidationError(_("Can't validate waybill without picking"))

            waybill._assign_l10n_ec_waybill_document_number()
            waybill.name = "GR {}".format(waybill.l10n_ec_waybill_document_number)
            waybill.l10n_ec_waybill_warehouse_id = waybill.location_id.warehouse_id

            # Create the respective electronic document
            ak = waybill._compute_l10n_ec_waybill_ak()

            xml_content = "<?xml version='1.0' encoding='UTF-8'?>" + str(waybill._l10n_ec_export_waybill_as_xml(ak))
            edi_values = {
                'state': 'to_send',
                'name': ak,
                'xml_content': xml_content,
                'model': 'ec.waybill',
                'res_id': waybill.id,
                'company_id': waybill.company_id.id,
                'ecu_document_type': '06',
            }

            waybill.env['l10nec.edi.document'].create(edi_values)

            waybill.state = 'waiting'

    def _prepare_export_edi_values(self, access_key):
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
            "access_key": access_key,
            "driver_partner_type": get_partner_type(self.driver_id),
            "environment": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.environment_type'),
            "issuing_type": self.env['ir.config_parameter'].sudo().get_param('l10n_ec_edi.issuing_type'),
        }

    def waybill_generate_xml(self):
        self.ensure_one()
        return b"<?xml version='1.0' encoding='UTF-8'?>" + self._export_waybill_as_xml()

    def _l10n_ec_export_waybill_as_xml(self, access_key):
        template_values = self._prepare_export_edi_values(access_key)
        content = self.env['ir.qweb']._render('l10n_ec_waybill.guia_remision', template_values)
        return content

    def action_view_edi_documents(self):
        action = self.env["ir.actions.actions"]._for_xml_id("l10n_ec_edi.l10n_ec_edi_document")
        action['domain'] = [('res_id', '=', self.id), ('model', '=', 'ec.waybill')]
        return action

    _sql_constraints = [
        ('waybill_document_number_uniq', 'UNIQUE (company_id, l10n_ec_waybill_document_number)', 'Waybill document number must be unique')
    ]


class EcWaybillPicking(models.Model):
    _name = 'ec.waybill.picking'
    _description = 'Ecuador Waybill Picking'

    name = fields.Char("Description", compute='_compute_name')

    l10n_ec_waybill_id = fields.Many2one(
        'ec.waybill',
        'Waybill',
        required=True
    )

    picking_id = fields.Many2one(
        'stock.picking',
        'Picking',
        required = True
    )

    l10n_ec_waybill_invoice_number = fields.Char("Invoice Number", related="picking_id.l10n_ec_waybill_invoice_number")

    l10n_ec_waybill_location_id = fields.Many2one(
        'stock.location',
        'Location', related="l10n_ec_waybill_id.location_id")

    l10n_ec_waybill_location_dest_id = fields.Many2one(
        'stock.location',
        'Dest. Location', related="picking_id.location_dest_id")

    @api.depends('picking_id')
    def _compute_name(self):
        """Compute name"""
        for record in self:
            record.name = "Transf. {}".format(record.picking_id.name)


class EcWaybillAdditionalInfo(models.Model):
    _name = 'ec.waybill.additional.info'
    _description = 'Ec Waybill Additional Info'

    waybill_id = fields.Many2one(
        'ec.waybill',
        'EcWaybill')
    key = fields.Char("Key")
    value = fields.Char("Value")

