# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError


import logging
import base64

_logger = logging.getLogger(__name__)


class ProcessBackupDetail(models.Model):
    _name = 'backup.process.detail'

    name = fields.Char(string="Name")
    file_name = fields.Char(string="File Name")
    backup_process_id = fields.Many2one(string="Backup Process Id", comodel_name="backup.process")
    file_path = fields.Char(string="File Path")
    url = fields.Char(string="Url")
    backup_date_time = fields.Datetime(string="Backup Time")
    status = fields.Char(string="Status")
    message = fields.Char(string="Message")

    def download_db_file(self):
        """
            Call by the download buttuon over every backup detail record.
            Method download the zip file of backup, 
        """

        file_path = self.file_path + self.file_name
        result = None
        with open(file_path , 'rb') as reader:
            result = base64.b64encode(reader.read())
        attachment_obj = self.env['ir.attachment'].sudo()
        name = self.file_name
        attachment_id = attachment_obj.create({
            'name': name,
            'datas': result,
            'public': False
        })
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'new',
        }
