# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        """
            colors :
                0  : none 
                1  : red
                10 : green
                2  : Orange
                3  : Yellow
                4  : Blue
                5  : Dark Purple
        """
        super(HelpdeskTicket, self)._compute_kanban_state_label()

        for ticket in self:
            if ticket.stage_id:
                if ticket.stage_id.id == self.env.ref("helpdesk.stage_on_hold").id:
                    ticket.color = 4
                elif ticket.stage_id.id == self.env.ref("helpdesk.stage_in_progress").id:
                    ticket.color = 10
                elif ticket.stage_id.id == self.env.ref("helpdesk.stage_done").id:
                    ticket.color = 1
                elif ticket.stage_id.id == self.env.ref("helpdesk.stage_cancelled").id:
                    ticket.color = 5
                else:
                    ticket.color = 0
            else:
                ticket.color = 0