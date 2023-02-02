# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_close_dialog(self):
        res = super(MailActivity, self).action_close_dialog

        if 'action_close_dialog' in self._context:
            task = self.env[self.res_model].browse(self.res_id)
            task.user_ids = False
            task.stage_id = self.env.ref("bfal_workflow.project_stage_not_accepted").id

        return res