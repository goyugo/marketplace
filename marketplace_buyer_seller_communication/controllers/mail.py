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
import base64
from odoo.tools import consteq, plaintext2html
import logging
_logger = logging.getLogger(__name__)

class MarketplaceBuyerSellerChatter(http.Controller):

    @http.route(['/mp/mail/chatter_post'], type='http', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        attachments = request.httprequest.files.getlist('attachments')
        url = request.httprequest.referrer
        if message:
            message = plaintext2html(message)
            record = request.env[res_model].sudo().browse(int(res_id))
            author_id = request.env.user.partner_id.id if request.env.user.partner_id else False
            kw.pop('attachments', None)
            msg = record.with_context(mail_create_nosubscribe=False).message_post(body=message,
                               message_type=kw.pop('message_type', "comment"),
                               subtype_xmlid=kw.pop('subtype', "mail.mt_comment"),
                               author_id=author_id,**kw)
            attachment_ids = []
            for file in attachments:
                attachment_dict = {
                    'attachment': file,
                }
                data = {
                    'attachments': []
                }
                for field_name, field_value in attachment_dict.items():
                    if hasattr(field_value, 'filename'):
                        field_name = field_name.rsplit('[', 1)[0]
                        field_value.field_name = field_name
                        data['attachments'].append(field_value)

                for file in data['attachments']:
                    if file.filename:
                        attachment_value = {
                            'name': file.filename,
                            'datas': base64.encodebytes(file.read()),
                            # 'datas_fname': file.filename,
                            'res_model': res_model,
                            'res_id': int(res_id),
                            'public':True
                        }
                        attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
                        attachment_ids.append(attachment_id.id)
            msg.attachment_ids = [(6,0, attachment_ids)]

            url = url + "#discussion"
        return request.redirect(url)
