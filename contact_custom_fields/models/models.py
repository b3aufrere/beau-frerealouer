# -*- coding: utf-8 -*-

from odoo import models, fields, api


class inheritcontact(models.Model):
    _inherit = 'res.partner'

    enter_date = fields.Date(string='Date entré')
    habita_type = fields.Many2one('res.habitat',string='Type habitation')
    mkg = fields.Float(default='1',string='MKG')
    client_type_maison = fields.Many2one('res.client.type',string='Type Client')
    black_liste = fields.Boolean(default=False)

    def _get_default_country(self):

        country = self.env['res.country'].search([('code', '=', 'CA')], limit=1)

        return country


    country_id = fields.Many2one('res.country', string='Country',

                                 default=_get_default_country)

    def _get_default_state(self):

        state = self.env['res.country.state'].search([('code', '=', 'QC')], limit=1)

        return state


    state_id = fields.Many2one('res.country.state', string='State',

                                 default=_get_default_state)



class reshabitat(models.Model):
    _name = 'res.habitat'

    name = fields.Char(string='Nom')

class restypeclient(models.Model):
    _name = 'res.client.type'

    name = fields.Char(string='Nom')