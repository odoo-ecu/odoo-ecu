odoo.define('l10n_ec_pos_accioma.models', function(require){
  "use strict";

  // var models = require('point_of_sale.models');
  //
  // models.load_fields('pos.config', ['invoice_prefix', 'invoice_highest_sequence'])
  // models.load_fields('pos.order', ['l10n_ec_authorization', 'l10n_ec_internal_number'])
  // var _super_order = models.Order.prototype
  // // console.log("models", models)
  //
  // models.Order = models.Order.extend({
  //   initialize: function(attr, options){
  //     var order = _super_order.initialize.apply(this, arguments)
  //     this.set_to_invoice(true)
  //   },
  //   set_l10n_latam_invoice_prefix: function(l10n_latam_invoice_prefix){
  //     this.l10n_latam_invoice_prefix = l10n_latam_invoice_prefix;
  //   },
  //   get_l10n_latam_invoice_prefix: function(){
  //     return this.l10n_latam_invoice_prefix;
  //   },
  //   set_l10n_ec_invoice_number: function(l10n_ec_internal_number){
  //     this.l10n_ec_internal_number = ('000000000' + l10n_ec_internal_number).slice(-9);
  //   },
  //   get_l10n_ec_internal_number: function(){
  //     return this.l10n_ec_internal_number
  //   },
  //
  //   export_for_printing: function() {
  //     var order = this.pos.get_order();
  //     var result = _super_order.export_for_printing.apply(this, arguments);
  //     result.l10n_latam_invoice_prefix = this.get_l10n_latam_invoice_prefix();
  //     result.l10n_latam_invoice_number = this.get_l10n_ec_internal_number();
  //     return result;
  //   }
  // })
  var { Order } = require('point_of_sale.models');
  var Registries = require('point_of_sale.Registries');

  const L10nEcOrder = (Order) => class L10nEcOrder extends Order {
    export_for_printing() {
      var result = super.export_for_printing(...arguments);
      result.customer = this.get_partner();
      console.log(result);
      return result;
    }
  }
  Registries.Model.extend(Order, L10nEcOrder);
});
