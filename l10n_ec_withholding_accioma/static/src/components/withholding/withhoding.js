/** @odoo-module **/

import { formatFloat, formatMonetary } from "@web/views/fields/formatters";
import { parseFloat } from "@web/views/fields/parsers";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

const { Component, onPatched, onWillUpdateProps, useRef, useState } = owl;

class WithholdingComponent extends Component{
    setup() {
        super.setup();
        this.withholdings = this.props.value;
        this.state = useState({ value: "readonly" });
    }
}

WithholdingComponent.template = "l10n_ec_withholding_accioma.WithholdingField";
WithholdingComponent.props = {
    ...standardFieldProps,
}

registry.category("fields").add("l10n-ec-withholding-accioma-field", WithholdingComponent);
