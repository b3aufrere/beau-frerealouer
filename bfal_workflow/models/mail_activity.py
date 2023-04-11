# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_close_dialog(self):
        res = super(MailActivity, self).action_close_dialog

        if 'is_from_task' in self._context:
            task = self.env[self.res_model].browse(self.res_id)
            task.user_ids = False
            new_stage_id = self.env['project.task.type'].search([('name', '=', 'Non accepté'), ('project_ids', 'in', self.project_id.id)], limit=1)
            
            if new_stage_id:
                task.stage_id = new_stage_id.id
            else:
                raise UserError("Il faut ajouté une étape Non accepté a ce projet")

        return res