# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api,_

class template_task(models.Model):

    _name = 'template.task'
    _rec_name = 'name'
  
    task_check = fields.Boolean(string="Project Check")
    name = fields.Char("Name",readonly=True,copy=False) 
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    
    @api.model
    def create(self,vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('template.task') or _('New')
        res = super(template_task, self).create(vals)
        return res

