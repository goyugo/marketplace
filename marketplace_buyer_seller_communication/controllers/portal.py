# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
import logging
_logger = logging.getLogger(__name__)

class PortalAccount(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalAccount, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        comm_count = request.env['buyer.seller.communication'].search_count([
            ('buyer_id', '=', partner.id),
        ])
        values['comm_count'] = comm_count
        return values

    # ------------------------------------------------------------
    # My Communication
    # ------------------------------------------------------------

    def _customer_comm_check_access(self, comm_id, access_token=None):
        customer_comm = request.env['buyer.seller.communication'].browse([comm_id])
        customer_comm_sudo = customer_comm.sudo()
        try:
            customer_comm.check_access_rights('read')
            customer_comm.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(customer_comm_sudo.access_token, access_token):
                raise
        return customer_comm_sudo

    def _customer_comm_get_page_view_values(self, customer_comm, access_token, **kwargs):
        values = {
            'page_name': 'customer_comm',
            'customer_comm': customer_comm,
        }

        if access_token:
            values['no_breadcrumbs'] = True
        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']
        return values

    @http.route(['/my/communications', '/my/communications/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_comm_request(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        CustomerComm = request.env['buyer.seller.communication']
        ProductPublicCategory = request.env['product.public.category'].sudo()
        CouintryStates = request.env['res.country.state'].sudo()

        domain = [
            ('buyer_id', '=', partner.id),
        ]

        searchbar_sortings = {
            'create_date': {'label': _('Create Date'), 'order': 'create_date desc'},
            'state': {'label': _('State'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        comm_count = CustomerComm.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/communications",
            url_args={'date_begin': date_begin, 'date_end': date_end,},
            total=comm_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        communications = CustomerComm.search(domain, limit=self._items_per_page, offset=pager['offset'], order=order)

        # Search Product Categories
        public_categ_ids = ProductPublicCategory.search([])

        # Search States
        country_id = request.env.ref('base.id', raise_if_not_found=False)
        if not country_id:
            country_id = request.env['res.country'].sudo().search([('code','=','ID')], limit=1)
        country_state_ids = CouintryStates.search([('country_id','=',country_id.id)])

        values.update({
            'date': date_begin,
            'communications': communications,
            'pager': pager,
            'default_url': '/my/communications',
            'page_name': 'customer_comm',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'public_categ_ids': public_categ_ids,
            'country_state_ids': country_state_ids,
        })
        if request.env['ir.default'].sudo().get('res.config.settings', 'group_mp_buyer_seller_comm'):
            return request.render("marketplace_buyer_seller_communication.portal_my_customer_comm", values)
        else:
            request.redirect("/")

    @http.route(['/my/communication/<int:comm_id>'], type='http', auth="user", website=True)
    def portal_my_comm_requests_detail(self, comm_id=None, access_token=None, **kw):
        customer_comm = request.env['buyer.seller.communication'].browse([comm_id])
        if not customer_comm.exists():
            return request.render('website.404')

        try:
            customer_comm_sudo = self._customer_comm_check_access(comm_id, access_token)
        except AccessError:
            return request.redirect('/my')

        values = self._customer_comm_get_page_view_values(customer_comm_sudo, access_token, **kw)

        if request.env['ir.default'].sudo().get('res.config.settings', 'group_mp_buyer_seller_comm'):
            return request.render("marketplace_buyer_seller_communication.portal_comm_requests_page", values)
        else:
            request.redirect("/")
