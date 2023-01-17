# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Territory(models.Model):
    _name = 'territory'
    _description = 'Territory'

    name = fields.Char(string="Nom", required=True)
    number = fields.Char(string="Numéro", required=True)
    index = fields.Char(string="Index", required=True)
    unit = fields.Char(string="Unité", required=True)
    entreprise_ids = fields.Many2many('entreprise', string="Entreprise(s)", required=True)
    link = fields.Char(string="Lien")
    map_image = fields.Binary(string="Map image")