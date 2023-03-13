odoo.define('l10n_ec_pos.L10nEcSequenceOnValidate', function(require){
  'use strict';

  const PaymentScreen = require('point_of_sale.PaymentScreen')
  const Registries = require('point_of_sale.Registries')

  const L10nEcSequenceOnValidate = PaymentScreen =>
    class extends PaymentScreen {
      async validateOrder(isForceValidate){
        // console.log(this.currentOrder)
        console.log('L10nEcSequenceOnValidate::validateOrder(): succesfully overriden')
        // console.log('config', this.env.pos.config)
        // console.log('db', this.env.pos.db)
        const l10n_latam_invoice_prefix = this.env.pos.config.invoice_prefix || "Doc. S/N";
        const l10n_ec_invoice_highest_sequence = this.env.pos.db.get_invoice_highest_sequence() > 0 ? this.env.pos.db.get_invoice_highest_sequence() : this.env.pos.config.invoice_highest_sequence
        const l10n_latam_invoice_number = l10n_ec_invoice_highest_sequence + 1;
        this.currentOrder.set_l10n_latam_invoice_prefix(this.env.pos.config.invoice_prefix || "Doc. S/N");
        this.currentOrder.set_l10n_ec_invoice_number(l10n_latam_invoice_number)
        this.env.pos.db.set_invoice_highest_sequence(l10n_latam_invoice_number)

        await super.validateOrder(isForceValidate)
      }
    }
  Registries.Component.extend(PaymentScreen, L10nEcSequenceOnValidate)
  return PaymentScreen
})
