/** @odoo-module */

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from 'web.utils';

patch(NavBar.prototype, "odoo_sidebar.NavBarMenu", {

    onToggleMenu(ev) {
        $('.o_main_navbar').toggleClass('o_main_navbar_shown');
    },

});