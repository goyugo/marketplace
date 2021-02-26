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

from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class WebsiteBuyerSellerComm(http.Controller):
    @http.route(['/inquiry'], type='http', auth="public", website=True)
    def mp_inquiry(self, redirect=None, resp=None, **kwargs):
        ProductPublicCategory = request.env['product.public.category'].sudo()
        CountryState = request.env['res.country.state'].sudo()

        # Search Product Categories
        categ = False
        try:
            categ_value = kwargs.get('categ', False)
            if categ_value:
                if type(eval(categ_value)) == int:
                    categ = eval(kwargs.get('categ', False))
        except Exception as e:
            pass

        public_categ_ids = ProductPublicCategory.search([('parent_id', '!=', False)])
        if categ:
            public_categ_ids = ProductPublicCategory.search([('parent_id', '=', categ)])

        # Search States
        country_id = request.env.ref('base.id', raise_if_not_found=False)
        if not country_id:
            country_id = request.env['res.country'].sudo().search([('code','=','ID')], limit=1)
        country_state_ids = CountryState.search([('country_id','=',country_id.id)])

        if not resp:
            resp = False
        values = request.params.copy()
        values.update({
            'public_categ_ids': public_categ_ids,
            'country_state_ids': country_state_ids,
            'resp': resp,
        })
        return request.render("marketplace_buyer_seller_communication.portal_inquiry", values)

    @http.route(['/submit/general-inquiries'], type='http', auth='public', website=True,)
    def submit_general_inquiries(self, **kwargs):
        if not request.env['ir.default'].sudo().get('res.config.settings', 'group_mp_buyer_seller_comm'):
            return request.redirect("/inquiry")
        if not request.env.user.has_group('base.group_portal'):
            return request.redirect("/inquiry?resp=portal")
        if request.env.user.has_group('odoo_marketplace.marketplace_draft_seller_group')\
            or request.env.user.has_group('odoo_marketplace.marketplace_seller_group'):
            return request.redirect("/inquiry?resp=seller")

        # Partner = request.env['res.partner'].sudo()
        category_id = int(kwargs['category_id']) if kwargs.get('category_id', False) else False
        if not category_id:
            return request.redirect("/my/communications/")
        state_id = int(kwargs['state_id']) if kwargs.get('state_id', False) else False

        # Verfied seller by Location and product category
        param = """ and pt.public_categ_id = %s""" %(category_id)
        if state_id:
            param += """ and rp.state_id = %s""" %(state_id)
        query = ("""SELECT
                rp.id AS partner_id
            FROM
                product_template AS pt
            LEFT JOIN
                res_partner AS rp
                ON rp.id = pt.marketplace_seller_id
            WHERE
                rp.seller=true
                and pt.status = 'approved'
                and rp.state='approved'
                %s
            GROUP BY
	            rp.id
            """) %(param)
        request._cr.execute(query)
        partner_ids = request.env.cr.fetchone()

        if not partner_ids:
            partner_ids = [3]
        for partner_id in list(partner_ids):
            values = {
                'buyer_id': request.env.user.partner_id.id,
                'marketplace_seller_id': partner_id,
                'subject': kwargs.get("subject"),
                'desc': kwargs.get("query_desc"),
                'state': 'open',
                'category_id': category_id,
                'state_id': state_id,
            }
            request.env['buyer.seller.communication'].sudo().create(values)
        return request.redirect("/my/communications/")

    @http.route(['/submit/communication'], type='http', auth='public', website=True,)
    def submit_communication(self, **kwargs):
        category_id = int(kwargs['category_id'])\
            if kwargs.get('category_id', False) else False
        product_id = int(kwargs['product_id'])\
            if kwargs.get('product_id', False) else False
        partner_id = request.env.user.partner_id.id
        values = {
            'buyer_id': partner_id,
            'marketplace_seller_id': int(kwargs.get("marketplace_seller_id")),
            'subject': kwargs.get("subject"),
            'desc': kwargs.get("query_desc"),
            'state': 'open',
            'product_id': product_id,
            'category_id': category_id,
        }
        comm_id = request.env['buyer.seller.communication'].sudo().create(values)

        # Remove wishlist
        wishlist_ids = request.env['product.wishlist'].sudo().current()
        if wishlist_ids:
            wishlist_ids.unlink()

        seller_url = kwargs.get("seller_url")
        return request.redirect("/my/communication/" + str(comm_id.id) or '/')
