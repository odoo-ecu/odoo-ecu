odoo.define('l10n_ec_pos_accioma.document_sequence', function(require){
  "use strict";

  var models = require('point_of_sale.models');

  models.load_fields('pos.config', ['invoice_prefix', 'invoice_highest_sequence'])
  models.load_fields('pos.order', ['l10n_ec_authorization', 'l10n_ec_internal_number'])
  var _super_order = models.Order.prototype
  console.log("models", models)

  models.Order = models.Order.extend({
    initialize: function(attr, options){
      var order = _super_order.initialize.apply(this, arguments)
      this.set_to_invoice(true)
    },
    set_l10n_latam_invoice_prefix: function(l10n_latam_invoice_prefix){
      this.l10n_latam_invoice_prefix = l10n_latam_invoice_prefix;
    },
    get_l10n_latam_invoice_prefix: function(){
      return this.l10n_latam_invoice_prefix;
    },
    set_l10n_ec_invoice_number: function(l10n_ec_internal_number){
      this.l10n_ec_internal_number = ('000000000' + l10n_ec_internal_number).slice(-9);
    },
    get_l10n_ec_internal_number: function(){
      return this.l10n_ec_internal_number
    },

    export_for_printing: function() {
      var order = this.pos.get_order();
      var result = _super_order.export_for_printing.apply(this, arguments);
      result.l10n_latam_invoice_prefix = this.get_l10n_latam_invoice_prefix();
      result.l10n_latam_invoice_number = this.get_l10n_ec_internal_number();
      return result;
    }
  })
});
