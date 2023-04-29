odoo.define('l10n_ec_pos_accioma.l10n_ec_pos_sequence', function(require, factory){
  'use strict'

  var models = require('point_of_sale.models')
  var DB = require('point_of_sale.DB')

  DB.include({
    init: function (options){
      this._super(options)
      this.invoice_highest_sequence = 0
    },
    get_invoice_highest_sequence: function(){
      return this.invoice_highest_sequence
    },
    set_invoice_highest_sequence: function(sequence){
      this.invoice_highest_sequence = sequence

    }
  })
})
