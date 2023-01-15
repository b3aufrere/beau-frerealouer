# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Entreprise(models.Model):
    _name = 'entreprise'
    _description = 'Entreprise'

    name = fields.Char(related='partner_id.name', string="Nom de l'entreprise", required=True, store=True, readonly=False)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string='Contact', required=True)
    street = fields.Char(compute='_compute_address', inverse='_inverse_street', string="Rue")
    street2 = fields.Char(compute='_compute_address', inverse='_inverse_street2', string="Rue 2")
    zip = fields.Char(compute='_compute_address', inverse='_inverse_zip', string="Code postal")
    city = fields.Char(compute='_compute_address', inverse='_inverse_city', string="Ville")
    state_id = fields.Many2one(
        'res.country.state', compute='_compute_address', inverse='_inverse_state',
        string="État", domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one('res.country', compute='_compute_address', inverse='_inverse_country', string="Pays")
    email = fields.Char(related='partner_id.email', store=True, readonly=False, string="Email")
    phone = fields.Char(related='partner_id.phone', store=True, readonly=False, string="Téléphone")
    mobile = fields.Char(related='partner_id.mobile', store=True, readonly=False, string="Mobile")
    website = fields.Char(related='partner_id.website', readonly=False, string="Site Web")

    def _inverse_street(self):
        for entreprise in self:
            entreprise.partner_id.street = entreprise.street

    def _inverse_street2(self):
        for entreprise in self:
            entreprise.partner_id.street2 = entreprise.street2

    def _inverse_zip(self):
        for entreprise in self:
            entreprise.partner_id.zip = entreprise.zip

    def _inverse_city(self):
        for entreprise in self:
            entreprise.partner_id.city = entreprise.city

    def _inverse_state(self):
        for entreprise in self:
            entreprise.partner_id.state_id = entreprise.state_id

    def _inverse_country(self):
        for entreprise in self:
            entreprise.partner_id.country_id = entreprise.country_id
    
    def _get_entreprise_address_field_names(self):
        return ['street', 'street2', 'city', 'zip', 'state_id', 'country_id']

    def _get_entreprise_address_update(self, partner):
        return dict((fname, partner[fname])
                    for fname in self._get_entreprise_address_field_names())

    def _compute_address(self):
        for entreprise in self.filtered(lambda entreprise: entreprise.partner_id):
            address_data = entreprise.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = entreprise.partner_id.browse(address_data['contact']).sudo()
                entreprise.update(entreprise._get_entreprise_address_update(partner))

    @api.model_create_multi
    def create(self, vals_list):
        # create missing partners
        no_partner_vals_list = [
            vals
            for vals in vals_list
            if vals.get('name') and not vals.get('partner_id')
        ]
        if no_partner_vals_list:
            partners = self.env['res.partner'].create([
                {
                    'name': vals['name'],
                    'is_company': True,
                    'email': vals.get('email'),
                    'phone': vals.get('phone'),
                    'website': vals.get('website'),
                    'country_id': vals.get('country_id'),
                }
                for vals in no_partner_vals_list
            ])
            # compute stored fields, for example address dependent fields
            partners.flush_model()
            for vals, partner in zip(no_partner_vals_list, partners):
                vals['partner_id'] = partner.id

        self.clear_caches()
        entreprises = super().create(vals_list)

        return entreprises