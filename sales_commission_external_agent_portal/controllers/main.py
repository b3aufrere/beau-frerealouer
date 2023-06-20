# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from collections import OrderedDict
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        sales_commission_obj = request.env['sales.commission']
        sales_commission_line_obj = request.env['sales.commission.line']
        if 'sales_commission_count' in counters:
            values['sales_commission_count'] = sales_commission_obj.sudo().search_count(
                [('commission_user_id', '=', partner.id)]
            )

        if 'sales_commission_line_count' in counters:
            values['sales_commission_line_count'] = sales_commission_line_obj.sudo().search_count(
                [('commission_user_id', '=', partner.id)]
            )
        return values
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        sales_commission_obj = request.env['sales.commission']
        sales_commission_line_obj = request.env['sales.commission.line']
        sales_commission_count = sales_commission_obj.sudo().search_count(
            [('commission_user_id', '=', partner.id)]
        )
        sales_commission_line_count = sales_commission_line_obj.sudo().search_count(
            [('commission_user_id', '=', partner.id)]
        )
        values.update({
            'sales_commission_count' : sales_commission_count,
            'sales_commission_line_count' : sales_commission_line_count,
        })
        return values
        
#    @http.route(['/my/commissions','/my/commissions/<int:page>'], type='http', auth="user", website=True)
    @http.route(['/my/commissions','/my/commissions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_commissions(self, page=1, sortby=None, filterby=None, search=None, search_in='content',**kw):
        values={}
        partner = request.env.user.partner_id
        sales_commission_obj = request.env['sales.commission']
        
        domain = [
            ('commission_user_id', '=', partner.id)
        ]
        
        sales_commission_count = sales_commission_obj.sudo().search_count(domain)
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Commission')},
            'state': {'input': 'state', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        # pager = request.website.pager(
        #     url="/my/commissions",
        #     url_args={'search_in': search_in, 'search': search},
        #     total=sales_commission_count,
        #     page=page,
        #     step=self._items_per_page
        # )
        pager = portal_pager(
            url="/my/commissions",
            url_args={'search_in': search_in, 'search': search},
            total=sales_commission_count,
            page=page,
            step=self._items_per_page
        )
        
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        
        sales_commission_ids = sales_commission_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'sales_commissions': sales_commission_ids,
            'page_name': 'sales_commission',
            'pager': pager,
            'default_url': '/my/commissions',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
        })
        
        return request.render("sales_commission_external_agent_portal.display_commission_worksheets", values)
        
    
    #@http.route(['/my/commissions/<int:commission>'], type='http', auth="user", website=True)
    @http.route(['/my/commissions/<model("sales.commission"):commission>'], type='http', auth="user", website=True)
    def portal_my_commission(self, commission=None, access_token=None, **kw):
        commission_id = request.env['sales.commission'].sudo().browse(commission.id)
        return request.render('sales_commission_external_agent_portal.portal_my_commission_worksheets', {'commission': commission_id})
        
        
#    @http.route(['/my/commission_lines','/my/commission_lines/<int:page>'], type='http', auth="user", website=True)
    @http.route(['/my/commission_lines', '/my/commission_lines/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_commission_lines(self, page=1, sortby=None, filterby=None, search=None, search_in='content',**kw):
        values={}
        partner = request.env.user.partner_id
        sales_commission_line_obj = request.env['sales.commission.line']
        
        domain = [
            ('commission_user_id', '=', partner.id)
        ]
        
        sales_commission_line_count = sales_commission_line_obj.sudo().search_count(domain)
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        
#        pager = request.website.pager(
#            url="/my/commission_lines",
#            url_args={'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
#            total=sales_commission_line_count,
#            page=page,
#            step=self._items_per_page
#        )
        
        pager = portal_pager(
            url="/my/commission_lines",
            url_args={'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=sales_commission_line_count,
            page=page,
            step=self._items_per_page
        )
        
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date desc'},
            'name': {'label': _('Commissions Line'), 'order': 'name'},
        }
        
        searchbar_inputs = {
            'line': {'input': 'line', 'label': _('Search in Commissions Line')},
            'state': {'input': 'state', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
    
#        sales_commission = request.env['sales.commission'].sudo().search([])
        sales_commission = request.env['sales.commission'].sudo().search([('commission_user_id', '=', partner.id)])
        for commission in sales_commission:
            searchbar_filters.update({
                str(commission.id): {'label': commission.name, 'domain': [('sales_commission_id', '=', commission.id)]}
            })
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ('line', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        
        sale_commission_line_ids = sales_commission_line_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'sales_commission_lines': sale_commission_line_ids,
            'page_name': 'sales_commission_line',
            'pager': pager,
            'default_url': '/my/commission_lines',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        
        return request.render("sales_commission_external_agent_portal.display_my_Commission_line", values)
        
    
    @http.route(['/my/commission_line/<model("sales.commission.line"):commission_line>'], type='http', auth="user", website=True)
    #@http.route(['/my/commission_line/<int:commission_line>'], type='http', auth="user", website=True)
    def portal_my_commission_line(self, commission_line=None, access_token=None, **kw):
        #values = {}
        commission_line_id = request.env['sales.commission.line'].sudo().browse(commission_line.id)
        return request.render('sales_commission_external_agent_portal.my_commission_line_view', {'commission_line': commission_line_id})
        
    
    #@http.route(['/commission_worksheet/print/<int:commission>'], type='http', auth="public", website=True)
    @http.route(['/commission_worksheet/print/<model("sales.commission"):commission>'], type='http', auth="public", website=True)
    def print_commission_worksheet(self, commission=None, **kwargs):
        if commission:
#            pdf, _ = request.env.ref('sales_commission_external_user.sales_commission_worksheet_report').sudo().render_qweb_pdf(commission.id)
            # pdf, _ = request.env.ref('sales_commission_external_user.sales_commission_worksheet_report').sudo()._render_qweb_pdf(commission.id)
            pdf = request.env['ir.actions.report']._render_qweb_pdf("sales_commission_external_user.sales_commission_worksheet_report", commission.id)[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/my/commissions')
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

