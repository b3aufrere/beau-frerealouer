# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Create Expense From Task",
    "author": "Softhealer Technologies",
    "website": "http://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Accounting",
    "summary": "Create Expense From Task Make Expense From Task Automatic Generate Expense From Task Produce Expenses From Task Expense From Project Task Expense While Create Task Odoo",
    "description": """Currently, in odoo, there is no feature to create expense while creating task. This module will help you to create expense from the task. You can see created expense using the smart button "Expense" from the task.""",
    "version": "16.0.1",
    "depends": [
        'project',
        'hr_expense',
    ],
    "data": [
        'views/project_views.xml',
        'views/hr_expense_views.xml',
    ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 15,
    "currency": "EUR"
}
