# -*- coding: utf-8 -*-
{
    'name': 'Beau-frere a louer Workflow',
    'version': '16.0.0.0.0',
    'license': 'OPL-1',
    
    'author': 'Kamel Benchehida',

    'depends': [
        'base', 
        'contacts', 
        'hr', 
        'crm', 
        'sale_project', 
        'sale_crm', 
        'sales_team',
        'calendar',
        'sale_timesheet',
        'industry_fsm',
        'project_enterprise',
        'industry_fsm_sale',
        'industry_fsm_report',
        'helpdesk',
        'mail',
        'timesheet_grid',
        'helpdesk_ticket_sale_order_ent',
        'branch',
        'product',
        'twilio_sms_gateway_gsc',
        'bi_crm_task',
        'sh_create_expense_from_task',
        'documents_project',
        'task_calendar_synch',
        'account'
    ],
    
    'data': [ 
        'security/security.xml',
        'security/ir.model.access.csv',
        
        'data/mail_template_accept_service.xml',
        'data/data.xml',
        
        'reports/report_layouts.xml',
        'reports/report_saleorder.xml',
        'reports/report_invoice.xml',

        'wizards/tip_assing_wizard.xml',

        'views/entreprise.xml',
        'views/division.xml',
        'views/territory.xml',
        'views/hr_employee.xml',
        'views/crm_lead.xml',
        'views/sale_order.xml',
        'views/project_task.xml',
        'views/mail_activity.xml',
        'views/account_move.xml',
        'views/branch.xml',
        'views/product.xml',
        'views/twilio_sms_gateway_account.xml',
        'views/crm_stage.xml',
        'views/task_cancellation_reason.xml',
        'views/order_not_accept_reason.xml',
        'views/res_config_settings.xml',
        'views/sale_template.xml',

        'wizards/reassignment.xml',
        'wizards/task_cancellation_wiz.xml',
        'wizards/order_not_accept_wiz.xml',
        
    ],

    'assets': {
        'web.assets_backend': [
            'bfal_workflow/static/src/js/tax.js',
            'bfal_workflow/static/src/xml/tax.xml'
        ],
        'web.assets_frontend': [
            'bfal_workflow/static/src/js/website.js',
        ]
    },
    
    'installable': True,
    'application' : True,
    'auto_install': False,
}
