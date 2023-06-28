odoo.define('bfal_workflow.website', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    const ajax = require('web.ajax');

    publicWidget.registry.ShowPassword = publicWidget.Widget.extend({
        selector: '#approve_with',
        events: {
            'click #approve_btn': '_on_approve_btn',
        },
        _on_approve_btn : async function(ev) {
            var tip_amount = $('#tip_selecte').val()
            var inv_id = $('#inv_id').val()

            const token = await ajax.jsonRpc('/invoice/tip', 'call', {
                tip_amount: tip_amount,
                inv_id: inv_id 
            });
            location.reload();
        }
    });

});