from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("state_id")
    def _onchange_state_city_id(self):
        if self.city_id and self.city_id.state_id != self.state_id:
            self.city_id = False
            self.city = False
            self.zip = False
