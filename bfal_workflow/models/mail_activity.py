# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

from logging import warning as w

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_close_dialog(self):
        w("mail >>>>>>>> action_close_dialog 1")
        res = super(MailActivity, self).action_close_dialog

        if 'is_from_task' in self._context:
            task = self.env[self.res_model].browse(self.res_id)
            new_stage_id = self.env['project.task.type'].search([('name', '=', 'Non accepté'), ('project_ids', 'in', task.project_id.id)], limit=1)
            
            if new_stage_id:
                task.stage_id = new_stage_id.id
                
                if task.sale_order_id:
                    w("mail >>>>>>>> action_close_dialog 2")
                    self.env['task.assignment.history'].create({
                        'order_id': task.sale_order_id.id,
                        'task_id': task.id,
                        'motif': self.summary,
                        'user_ids': [(6, 0, [user.id for user in task.user_ids])] if task.user_ids else False
                    })
                    
                task.user_ids = False
            else:
                raise UserError("Il faut ajouté une étape Non accepté a ce projet")

        return res