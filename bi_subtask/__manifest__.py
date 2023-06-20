# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Task Delegation and Subtasks Odoo',
    'version': '16.0.0.1',
    'category': 'Project',
    'summary': 'Apps use for Project task Subtasks management and Task Delegation project subtask project sub task tracking project sub-tasks task allocation Task SubTask Checklist Task checklist Add Subtasks on Project Task Add Subtasks on task Custom task customize task',
    'price': 10.00,
    'currency': "EUR",
    'description': """

BrowseInfo developed a new odoo/OpenERP module apps
task tracking Task Delegation and Subtasks Task and Subtasks task management subtasks
project subtasks project task project sub-tasks
task allocation task Project Task SubTask Checklist
Task SubTask Checklis SubTask Checklist
Add Subtasks on Project Task Add Subtasks on task
Custom task Custom project Customized task Divide task Custom Project management. 
Sub-task for task Parent child task Subtask Management on Project Delegation on Task Issue ticket 
Task tickit Add task improve task management divide task task break system task divide on sub tasks
project divide tasks divide subtasks project phase subtasks project phase sub-tasks 
""",

    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'images': [],
    'depends': ['base', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/task.xml',
        'views/res_config_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://youtu.be/bp7QLc_zEAg',
    "images": ['static/description/Banner.gif'],
    'license': 'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
