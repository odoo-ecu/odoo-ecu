from odoo import _, api, fields, models, tools

class AccountMove(models.Model):

    _inherit = 'account.move'

    def action_create_waybill(self):
        """Create new waybill based on invoice"""
        waybill_vals = {

        }

        waybill = self.env['ec.waybill'].sudo().create()
        cash_rounding_line = self.env['account.move.line'].create(rounding_line_vals)

        for invoice in self:
            pass
