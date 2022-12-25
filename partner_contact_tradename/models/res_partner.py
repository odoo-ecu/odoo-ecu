# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tradename = fields.Char('Nombre comercial', size=300, )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        try:
            recs = self.search(['|','|', ('tradename', operator, name), ('name', operator, name), ('vat', operator, name)] + args, limit=limit)
        except:
            recs = self.search(['|', ('tradename', operator, name), ('name', operator, name)] + args, limit=limit)
        return recs.name_get()
