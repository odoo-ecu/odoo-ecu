odoo.define('l10n_ec.withholding', function (require) {
  "use strict"

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var field_registry = require('web.field_registry');
var field_utils = require('web.field_utils');

var QWeb = core.qweb;
var _t = core._t;

var ShowWithholdingLineWidget = AbstractField.extend({
});


field_registry.add('withholding', ShowWithholdingLineWidget);

