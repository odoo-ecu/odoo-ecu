# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import base64
from datetime import datetime,date,timedelta
from odoo.tools import ustr
from io import StringIO
import io
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class RouteLocation(models.Model):
    _name  = 'route.location'
    _description = 'Route Location'

    name =  fields.Char('Location Name')

class TransportLocationDetails(models.Model):

    _name = 'transport.location.details'
    _description = 'Transport Location Details'

    source_loc = fields.Many2one('route.location', 'Source Location')
    dest_loc  = fields.Many2one('route.location','Destination Location')
    distance = fields.Float('Distance (KM)')
    time   = fields.Float('Time in Hours')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    note  = fields.Char('Comment')
    tracking_number  =  fields.Char('Tracking Number')
    picking_id = fields.Many2one('stock.picking')
    transport_entry_id = fields.Many2one('transport.entry')
    route_id = fields.Many2one('transport.route', 'Route Of Transportation')
    state = fields.Selection([('draft', 'Start'), ('waiting','Waiting'),('in-progress', 'In-Progress'),('done','Done'),('cancel','Cancel')] , 'State',default='draft')
    transport_charge = fields.Float(string='Transport Charges', compute='_compute_charges')

    @api.depends('distance', 'route_id.transporter_id.transport_charge')
    def _compute_charges(self):
        for i in self:
            i.transport_charge = (i.route_id.transporter_id.transport_charge or 0.0) * i.distance

class TransportRoute(models.Model):
    _name  = 'transport.route'
    _description = 'Transport Route'

    name = fields.Char('Name')
    # transporter_id  = fields.Many2one('transport','Transporter')
    # route_locations_ids  =  fields.One2many('transport.location.details', 'route_id', 'Route Lines')
