/** @odoo-module **/

import { TaxTotalsComponent } from "@account/components/tax_totals/tax_totals"
import { patch } from "@web/core/utils/patch";
import { formatFloat, formatMonetary } from "@web/views/fields/formatters";

console.log("/TaxTot1111111alsComponent", TaxTotalsComponent)

patch(TaxTotalsComponent.prototype, 'bfal_workflow.bfal_workflow', {
    // Use the regex given by the session, else use an impossible one
    formatData(props) { 
        let rec = this._super(props)
        const currencyFmtOpts = { currencyId: props.record.data.currency_id && props.record.data.currency_id[0] };
        if (this.totals.tip_value){
            this.totals.amount_total += this.totals.tip_value
            this.totals.formatted_amount_total = formatMonetary(this.totals.amount_total, currencyFmtOpts);
        }
        return rec
    }
});
