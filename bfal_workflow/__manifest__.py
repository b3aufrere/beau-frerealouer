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
        'industry_fsm',
        'project_enterprise',
        'industry_fsm_sale',
        'industry_fsm_report',
        'helpdesk',
        'mail',
        'timesheet_grid'
    ],
    
    'data': [ 
        'security/ir.model.access.csv',
        
        'data/mail_template_accept_service.xml',
        'data/data.xml',

        # 'reports/report_saleorder.xml',

        'views/entreprise.xml',
        'views/division.xml',
        'views/territory.xml',
        'views/hr_employee.xml',
        'views/crm_lead.xml',
        'views/sale_order.xml',
        'views/project_task.xml',
        'views/mail_activity.xml'
    ],
    
    'installable': True,
    'application' : True,
    'auto_install': False,
}
