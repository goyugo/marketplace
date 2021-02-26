# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Odoo Marketplace Buyer Seller Communication",
  "summary"              :  """Odoo Marketplace Buyer Seller Communication facilitates seller to communicate with the buyer in Odoo Marketplace.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Buyer-Seller-Communication.html",
  "description"          :  """Customer chat support
Customer support system
Buyer seller messages
buyer-seller messaging service
Odoo chat support
Marketplace customer messages
Odoo marketplace buyer queries
Odoo buyer questions
Communicate with seller
Send message to seller
Seller message send
Odoo Marketplace
Odoo multi vendor Marketplace
Multi seller marketplace
Multi-seller marketplace
multi-vendor Marketplace""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_buyer_seller_communication&lifetime=120&lout=1&custom_url=/",
  "depends"              :  ['odoo_marketplace'],
  "data"                 :  [
                             'security/access_control_security.xml',
                             'security/ir.model.access.csv',
                             'data/data.xml',
                             'views/templates.xml',
                             'views/buyer_seller_communication_view.xml',
                             'views/mp_config_view.xml',
                             'views/mp_seller_view.xml',
                             'views/inherit_seller_profile_template.xml',
                             'views/portal_account_communication_templates.xml',
                             'data/mp_buyer_seller_comm_data.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}