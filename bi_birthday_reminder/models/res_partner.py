# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.http import request


class res_partner(models.Model):
	_inherit = "res.partner"

	birthdate = fields.Date(string='Date Of Birth')

	@api.model
	def _cron_birthday_reminder(self):
		uid = self.env.user.id
		su_id =self.env['res.partner'].browse(SUPERUSER_ID)
		for partner in self.search([]):
			if partner.birthdate:
				bdate =datetime.strptime(str(partner.birthdate),'%Y-%m-%d').date()
				today =datetime.now().date()
				if bdate.month == today.month:
					if bdate.day == today.day:
						if partner:
							template_id = self.env['ir.model.data']._xmlid_to_res_id('bi_birthday_reminder.email_template_edi_birthday_reminder', raise_if_not_found=False)
							template_browse = self.env['mail.template'].browse(template_id)
							if template_browse:
								values = template_browse.generate_email(partner.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date','attachment_ids'])
								values['email_from'] = su_id.email
								values['email_to'] = partner.email
								values['author_id'] =self.env.user.id
								values['res_id'] = False
								values['user_id'] = uid
								if not values['email_to'] and not values['email_from']:
									pass
								msg_id = self.env['mail.mail'].create({
									'email_to': values['email_to'],
									'auto_delete': True,
									'email_from':values['email_from'],
									'subject':values['subject'],
									'body_html':values['body_html'],
									'author_id':values['user_id']})
								mail_mail_obj = self.env['mail.mail']
								if msg_id:
									mail_mail_obj.sudo().send(msg_id)
		return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
