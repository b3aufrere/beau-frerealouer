odoo.define('bfal_workflow.website', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    const ajax = require('web.ajax');

    publicWidget.registry.ShowPassword = publicWidget.Widget.extend({
        selector: '#approve_with',
        events: {
            'click #approve_btn': '_on_approve_btn',
            'change #tip_selecte': '_onchangeTipSelecte',
        },
        _on_approve_btn : async function(ev) {
            var tip_percent = $('#tip_selecte').val()
            var inv_id = $('#inv_id').val()
            var tip_amount = $('#tip_amount').val()

            const token = await ajax.jsonRpc('/invoice/tip', 'call', {
                tip_percent: tip_percent,
                tip_amount: tip_amount,
                inv_id: inv_id 
            });
            location.reload();
        },

        _onchangeTipSelecte : function(ev) {
            if ($("#tip_selecte").val()  != "-1") {
                $("#tip_amount").hide();
                $("#tip_amount").reset();
            }
            else {
                $("#tip_amount").show();
            } 
        }
    });

});