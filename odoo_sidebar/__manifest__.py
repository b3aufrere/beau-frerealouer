# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Responsive Sidebar',
    'version': '16.0.1.0.0',
    'live_test_url': 'https://youtu.be/HUbAghadZyM',
    'sequence': 1,
    'summary': """
        Odoo Backend Theme, Odoo Community Backend Theme, Web backend Theme, Web Responsive Odoo Theme, New theme design, New design, 
        Web Responsive Odoo Backend Theme, Odoo Theme, Odoo Modern Theme, Odoo Modern Backend Theme Odoo, Advance Theme Backend Advanced,
        All in one, New advanced Odoo Menu, Sidebar apps, New design, Left sidebar menu, Web menu, Odoo backend menu, Web Responsive menu,
        Advance Menu Odoo App Menu Apps, Advanced Apps Menu, Elegant Menu, Menuitem, Web App Menu Backend, Menu Odoo Backend, Collapse Menu,
        Expand Menu, Collapsed Menu, Expanded Menu, New Style Menus, Advanced Sidebar Menu, Advance Sidebar Menu, Responsive Menu Sidebar, 
        Responsive Sidebar, Hide menu, Show Menu, Hide Sidebar, Show Sidebar, Toggle Menu, Toggle Sidebar, All in one Dynamic Menu Access,
        Visibility Menu Visibility, Quick Backend Menu, Dropdown Menu, Parent Menus, Shortcut Menus Shortcut, Menu Icons, Collapsible menu Odoo,
        Customize Menu Customize Sidebar App, Customization Menu Customization App Sidebar Customization Sidebar Apps, Group Left Menu in Odoo,
        Global Search Menu Search, Global Menu Access Global Apps Menu Global, Group Top Menu in Odoo, Odoo Foldable Menu Applications, Navbar,
        App web Menu, Quick Menu Access Menu, Menu Dynamic Sidebar, Any menu, Easy Access for menuitems, User Menu Users, All in one Sidebar,
        Advanced Menu, Advanced Odoo Menu Backend Odoo Web Theme Web Odoo, Elegant Theme Simple Theme, Advance List View Manager, Menu Style,
        Advanced List View Advanced Pivot View Theme Table View Theme Form View Theme Advanced Forms, Beautiful Theme Design, New Style Menu Theme Menu
    """,
    'description': "It's time to bid goodbye to the boring, monotonous sidebar of Odoo which you have been using for a while and say hello to a new sidebar, which breathes life into your Odoo backend and one that you can customize and make new every day.",
    'author': 'NEWAY Solutions',
    'maintainer': 'NEWAY Solutions',
    'price': '19.9',
    'currency': 'EUR',
    'website': 'https://neway-solutions.com',
    'license': 'OPL-1',
    'images': [
        'static/description/wallpaper.png'
    ],
    'depends': [
        'web'
    ],
    'data': [
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_sidebar/static/src/scss/variable.scss',
            'odoo_sidebar/static/src/scss/global.scss',
            'odoo_sidebar/static/src/scss/menu.scss',
            'odoo_sidebar/static/src/js/navbar.js',
            'odoo_sidebar/static/src/xml/sidebar.xml',
        ],
    },
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
