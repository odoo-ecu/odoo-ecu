/** @odoo-module **/
const {xml, Component} = owl;

import { standardFieldProps } from '@web/views/fields/standard_field_props'

import {registry} from '@web/core/registry'

export class CodeField extends Component {
    setup() {

        super.setup();
    }

}
CodeField.template = xml`<pre t-out="props.value" class="bg-primary text-white p-3 rounded" />`;
CodeField.props = standardFieldProps;

registry.category("fields").add("code", CodeField)


