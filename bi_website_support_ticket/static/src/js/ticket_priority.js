odoo.define('bi_website_support_ticket.bi_website_support_ticket', function (require) {
'use strict';
	require('web.dom_ready');
	var core = require('web.core');
	var ajax = require('web.ajax');
	var rpc = require('web.rpc');
	var request
	var _t = core._t;
	$(document).ready(function(){
		var priority_value = $('#priority_value').val()
		$('#ticket_priority').val(priority_value)
	});
});