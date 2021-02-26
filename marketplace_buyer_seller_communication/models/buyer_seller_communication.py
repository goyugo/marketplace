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

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
import logging
_logger = logging.getLogger(__name__)

class BuyerSellerCommunication(models.Model):
    _name = "buyer.seller.communication"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "A new Buyer Seller Communication is "
    _rec_name = "buyer_id"
    _order = "id desc"

    buyer_id = fields.Many2one("res.partner", string="Send By", required=True,tracking=True,)
    marketplace_seller_id = fields.Many2one("res.partner", string="Seller", required=True,tracking=True,)
    subject = fields.Char("Subject", required=True, tracking=True,)
    state = fields.Selection([
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ], "State", default="open", required=True, tracking=True,)
    desc = fields.Text("Description", required=True)
    resolved_date = fields.Date("Resolved On")
    closed_date = fields.Date("Closed On")
    name = fields.Char("")
    product_id = fields.Many2one('product.template', string='Product')
    category_id = fields.Many2one('product.public.category')
    state_id = fields.Many2one('res.country.state', string='Province', related="marketplace_seller_id.state_id", store=True)
    # custom
    new_inquiry = fields.Boolean(string='New Inquiry')

    def button_set_to_resolved(self):
        for rec in self:
            rec.resolved_date = date.today()
            rec.write({'state':'resolved'})
        return True

    def button_set_to_closed(self):
        for rec in self:
            rec.closed_date = date.today()
            rec.write({'state': 'closed'})
        return True

    def _add_mail_followers(self, buyer_id, marketplace_seller_id):
        for rec in self:
            if buyer_id not in rec.message_partner_ids.ids:
                rec.message_subscribe([buyer_id])
            if marketplace_seller_id not in rec.message_partner_ids.ids:
                rec.message_subscribe([marketplace_seller_id])
        return

    @api.model
    def create(self, vals):
        res= super(BuyerSellerCommunication, self).create(vals)
        if vals.get("buyer_id") and vals.get("marketplace_seller_id"):
            if vals.get("buyer_id") == vals.get("marketplace_seller_id"):
                raise UserError(_("Buyer and Seller cannot be same"))
        res._add_mail_followers(vals.get("buyer_id"), vals.get("marketplace_seller_id"))
        # custom
        res.new_inquiry = True
        return res

    def write(self, vals):
        res= super(BuyerSellerCommunication, self).write(vals)
        for rec in self:
            buyer_id = vals.get("buyer_id") if vals.get("buyer_id") else rec.buyer_id.id
            marketplace_seller_id = vals.get("marketplace_seller_id") if vals.get("marketplace_seller_id") else rec.marketplace_seller_id.id
            if buyer_id == marketplace_seller_id:
                raise UserError(_("Buyer and Seller cannot be same"))
            rec._add_mail_followers(buyer_id, marketplace_seller_id)
        return res
    
    # custom
    def _send_new_inquiry_mail(self):
        try:
            _logger.warning("=====> Sending new inquiry notification to %s <======\n" %(self.marketplace_seller_id.name))
            template_obj = self.env.ref(
                'marketplace_buyer_seller_communication.new_inquiry_email_template_for_seller',
                raise_if_not_found=False)
            template_obj.with_company(self.env.company).send_mail(self.id, True)
            self.new_inquiry = False
            _logger.warning("=====> New inquiry notification is sent to %s <======\n" %(self.marketplace_seller_id.name))
        except Exception as e:
            _logger.warning("""=====> Failed sending New inquiry notification to %s. <====="""\
                %(self.marketplace_seller_id.name))

    def _cron_send_new_inquries(self):
        inquiry_ids = self.search([('new_inquiry','=',True)])
        _logger.warning("""=====> Searching for new inquiries %s. <====="""\
            %(str(inquiry_ids)))
        for inquiry in inquiry_ids:
            inquiry._send_new_inquiry_mail()
