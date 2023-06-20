# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.osv import expression

class ResBranch(models.Model):
    _inherit = 'res.branch'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string="Société", required=True)

    active = fields.Boolean(default=True)
    division_id = fields.Many2one('division', string='Division', required=True)
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
    company_registry = fields.Char(related='partner_id.company_registry', readonly=False, string="ID de la société")

    def _inverse_street(self):
        for branch in self:
            branch.partner_id.street = branch.street

    def _inverse_street2(self):
        for branch in self:
            branch.partner_id.street2 = branch.street2

    def _inverse_zip(self):
        for branch in self:
            branch.partner_id.zip = branch.zip

    def _inverse_city(self):
        for branch in self:
            branch.partner_id.city = branch.city

    def _inverse_state(self):
        for branch in self:
            branch.partner_id.state_id = branch.state_id

    def _inverse_country(self):
        for branch in self:
            branch.partner_id.country_id = branch.country_id
    
    def _get_entreprise_address_field_names(self):
        return ['street', 'street2', 'city', 'zip', 'state_id', 'country_id']

    def _get_entreprise_address_update(self, partner):
        return dict((fname, partner[fname])
                    for fname in self._get_entreprise_address_field_names())

    def _compute_address(self):
        for branch in self.filtered(lambda branch: branch.partner_id):
            address_data = branch.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = branch.partner_id.browse(address_data['contact']).sudo()
                branch.update(branch._get_entreprise_address_update(partner))

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
                    'company_registry': vals.get('company_registry')
                }
                for vals in no_partner_vals_list
            ])
            # compute stored fields, for example address dependent fields
            partners.flush_model()
            for vals, partner in zip(no_partner_vals_list, partners):
                vals['partner_id'] = partner.id

        self.clear_caches()
        branchs = super().create(vals_list)

        return branchs