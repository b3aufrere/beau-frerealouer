# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Division(models.Model):
    _name = 'division'
    _description = 'Division'

    name = fields.Char(string="Nom", required=True)
    entreprise_ids = fields.One2many('entreprise', 'division_id', string='Entreprise(s)')