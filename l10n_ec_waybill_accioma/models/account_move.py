from odoo import _, api, fields, models, tools

class AccountMove(models.Model):

    _inherit = 'account.move'

    def action_create_waybill(self):
        """Show wizard for waybill creation"""

        view_id = self.env.ref('l10n_ec_waybill_accioma.create_waybill_from_invoice_wiz_view_form').id
        return {
            'name': _('Create Waybill'),
            'type': 'ir.actions.act_window',
            'res_model': 'l10n.ec.cwfi.wiz',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
        }
