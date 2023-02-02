# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.depends('stage_id')
    def _compute_ticket_color(self):
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
        for ticket in self:
            if ticket.stage_id:
                if ticket.stage_id.id == self.env.ref("helpdesk.stage_on_hold").id:
                    ticket.color = 4
                elif ticket.stage_id.id == self.env.ref("helpdesk.stage_in_progress").id:
                    ticket.color = 10
                elif ticket.stage_id.id == self.env.ref("helpdesk.stage_done").id \
                        or ticket.stage_id.id == self.env.ref("helpdesk.stage_solved").id:
                    ticket.color = 1
                elif ticket.stage_id.id == self.env.ref("	helpdesk.stage_cancelled").id:
                    ticket.color = 5
                else:
                    ticket.color = 0
            else:
                ticket.color = 0