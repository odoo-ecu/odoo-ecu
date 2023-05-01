import logging
from odoo import _, fields, models, api
from datetime import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class L10nEcCwfiWiz(models.TransientModel):

    _name = 'l10n.ec.cwfi.wiz'
    _description = 'Create Waybill from Invoice'

    date = fields.Datetime('Transport Date',default = datetime.now(), copy=False, required=True)
    date_due = fields.Datetime('Transport Due Date',default = datetime.now(), copy=False, required=True)
    note = fields.Text('Note', copy=False)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Transport Vehicle', required=True)
    driver_id = fields.Many2one('res.partner', 'Vehicle Driver', required=True)
    location_id = fields.Many2one('stock.location', string='Source Location', domain=[('usage', '=', 'internal')], required=True)

    invoice_ids = fields.Many2many('account.move', 'account_move_l10n_ec_cwfi_rel', string='Invoices')

    route_id = fields.Many2one('transport.route', string='Route')
    transport_reason = fields.Char("Transport Reason", default=_("Sale"))


    @api.model
    def default_get(self, fields):
        res = super(L10nEcCwfiWiz, self).default_get(fields)
        res_ids = self._context.get('active_ids')

        invoices = self.env['account.move'].browse(res_ids).filtered(lambda move: move.is_invoice(include_receipts=True))
        if not invoices:
            raise UserError(_("You can only create waybills from invoices."))

        # This is not working, error: int object is not suscriptable
        # res.update({
        #     'invoice_ids': res_ids,
        # })

        return res

    def _prepare_create_waybill_line_values(self):
        self.ensure_one()
        res = []
        res_ids = self._context.get('active_ids')

        invoices = self.env['account.move'].browse(res_ids).filtered(lambda move: move.is_invoice(include_receipts=True))
        if not invoices:
            raise UserError(_("You can only create waybills from invoices."))

        for invoice_id in res_ids:
            res.append((0, 0, {
                "invoice_id": invoice_id,
                "route_id": self.route_id.id,
                "transport_reason": self.transport_reason,
            }))

        return res

    def _prepare_create_waybill_values(self):
        self.ensure_one()
        res = {
            "date": self.date,
            "date_due": self.date_due,
            "note": self.note,
            "vehicle_id": self.vehicle_id.id,
            "driver_id": self.driver_id.id,
            "location_id": self.location_id.id,
            "picking_ids": self._prepare_create_waybill_line_values()
        }
        _logger.info("Values: {}".format(res))
        return res

    def action_create_waybill(self):
        """Create and return waybill"""
        self.ensure_one()
        waybill = self.env['ec.waybill'].create(
            self._prepare_create_waybill_values()
        )

        action = waybill.get_formview_action()
        action['domain'] = [('id', '=', "waybill.id")]
        action['view_mode'] = "tree,form"
        return action
