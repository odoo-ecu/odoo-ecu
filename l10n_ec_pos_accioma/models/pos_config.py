# -*- encoding: utf-8 -*-
# Copyright 2021 Accioma (https://accioma.com).
# @author marcelomora <java.diablo@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

class PosConfig (models.Model):
    _inherit = 'pos.config'
    
    api.depends('invoice_journal_id')
    def _compute_invoice_sequence(self):
        sql = """
            SELECT sequence_prefix, sequence_number
            FROM account_move
            WHERE journal_id = %s
            AND move_type = 'out_invoice'
            ORDER BY sequence_number desc limit 1;
        """

        for rec in self:
            self.env.cr.execute(sql, (rec.invoice_journal_id.id, ))
            res = self.env.cr.fetchone()
            
            rec.invoice_prefix = res[0]
            rec.invoice_highest_sequence = res[1]

    invoice_prefix = fields.Char("Invoice Prefix", compute='_compute_invoice_sequence')
    invoice_highest_sequence = fields.Integer("Highest sequence", compute='_compute_invoice_sequence')


    
    

