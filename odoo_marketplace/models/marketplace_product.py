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
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Default methods
    def _get_default_category_id(self):
        if self.marketplace_seller_id:
            mp_categ = self.env['res.config.settings'].get_mp_global_field_value('internal_categ')
            if mp_categ:
                return mp_categ
        elif self._context.get("pass_default_categ"):
            return False
        return super(ProductTemplate, self)._get_default_category_id()

    # Fields declaration

    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id,
        required=True, help="Select category for the current product")
    status = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), (
        'approved', 'Approved'), ('rejected', 'Rejected')], "Marketplace Status", default="draft", copy=False, tracking=True)
    qty = fields.Float(string="Initial Quantity",
                       help="Initial quantity of the product which you want to update in warehouse for inventory purpose.", copy=False)
    template_id = fields.Many2one(
        "product.template", string="Product Template Id", copy=False)
    marketplace_seller_id = fields.Many2one(
        "res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'], copy=False, tracking=True, help="If product has seller then it will consider as marketplace product else it will consider as simple product.")
    state_id = fields.Many2one('res.country.state', string="Province", related='marketplace_seller_id.state_id', store=True)
    color = fields.Integer('Color Index')
    pending_qty_request = fields.Boolean(
        string="Request Pending", compute="_get_pending_qty_request")
    is_initinal_qty_set = fields.Boolean("Initial Qty Set")
    activity_date_deadline = fields.Date(
        'Next Activity Deadline', related='activity_ids.date_deadline',
        readonly=True, store=True,
        groups="base.group_user,odoo_marketplace.marketplace_seller_group")
    item_ids = fields.One2many('product.pricelist.item', 'product_tmpl_id', 'Pricelist Items')
    # custom
    # originally
    # public_categ_ids = fields.Many2many('product.public.category')
    # public_categ_ids = fields.Many2many('product.public.category', compute='_compute_public_categ_ids')
    public_categ_id = fields.Many2one('product.public.category', string='Category')
    keyword_ids = fields.Many2many('product.keyword', string='Keywords', help="Max. 5 keywords")
    page_views_count = fields.Integer(string='Page Views', compute='_page_views_count')
    production_capacity = fields.Float(string='Production Capacity')
    minimum_order = fields.Float(string='Minimum Order')
    uom_text = fields.Char(string='Unit of Measures', default='Unit', help='Unit of Measures')
    # project
    project = fields.Boolean(string='Project')
    project_sector = fields.Char(string='Field / Sector')
    project_location = fields.Text(string='Project Location')
    project_portofolio_ids = fields.One2many('project.portofolio', 'project_id', 'Project Portofolio')
    currency_id = fields.Many2one(store=True, readonly=False)
    seller_state = fields.Selection(string="Seller Status", related='marketplace_seller_id.state', store=True, tracking=True)
    # project address fields
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    @api.depends('company_id')
    def _compute_currency_id(self):
        res = super(ProductTemplate, self)._compute_currency_id()
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id
            if template.project:
                currency_id = self.env.ref('base.USD') or currency_id
            template.currency_id = currency_id
        return res

    @api.depends('public_categ_id')
    def _compute_public_categ_ids(self):
        for rec in self:
            rec.public_categ_ids = [rec.public_categ_id.id] if rec.public_categ_id else []

    @api.onchange('marketplace_seller_id')
    def _onchange_public_categ_id(self):
        if self.marketplace_seller_id:
            if self.marketplace_seller_id.project_seller\
                and self.marketplace_seller_id.project_type_id:
                self.public_categ_id = self.marketplace_seller_id.project_type_id

    @api.constrains('public_categ_ids')
    def validate_categ_ids(self):
        if len(self.public_categ_ids.ids) > 1:
            raise ValidationError('You can not choose more than one category.')

    @api.constrains('keyword_ids')
    def validate_keyword_ids(self):
        if len(self.keyword_ids.ids) > 5:
            raise ValidationError('Can not add keywords more than 5.')

    def _page_views_count(self):
        for rec in self:
            track_count = 0
            for product in rec.product_variant_ids:
                track_count += len(self.env['website.track'].search([('product_id', '=', product.id)]))
            rec.page_views_count = track_count
    ###

    @api.model
    def _read_group_fill_results( self, domain, groupby, remaining_groupbys,
        aggregated_fields, count_field,read_group_result, read_group_order=None):

        if groupby == 'status':
            for result in read_group_result:
                state = result['status']
                if state in ['rejected']:
                    result['__fold'] = True
        return super(ProductTemplate, self)._read_group_fill_results(domain, groupby, remaining_groupbys,
            aggregated_fields, count_field, read_group_result, read_group_order)

    # SQL Constraints

    # compute and search field methods, in the same order of fields declaration

    @api.model
    def _get_pending_qty_request(self):
        for obj in self:
            mp_stock_obj = self.env["marketplace.stock"].search(
                [('product_temp_id', '=', obj.id), ('state', '=', 'requested')])
            obj.pending_qty_request = True if mp_stock_obj else False

    # Constraints and onchanges

    @api.onchange("marketplace_seller_id")
    def onchange_seller_id(self):
        self.status = "draft" if self.marketplace_seller_id and not self.status else False
        self.categ_id = self.env['res.config.settings'].get_mp_global_field_value('internal_categ')

    # CRUD methods (and name_get, name_search, ...) overrides

    @api.model
    def create(self, vals):
        ''' Set default false to sale_ok and purchase_ok for seller product'''
        partner = self.env["res.partner"].sudo().browse(vals.get("marketplace_seller_id", False)) or self.env.user.partner_id
        if partner and partner.sudo().seller:
            if not vals.get("sale_ok", False):
                vals["sale_ok"] = False
            if not vals.get("purchase_ok", False):
                vals["purchase_ok"] = False
            if not vals.get("status", False):
                vals["status"] = "draft"
            if vals.get('type', False) and vals['type'] != 'service' and not vals.get("invoice_policy", False):
                vals["invoice_policy"] = "delivery"
            mp_categ = self.env['res.config.settings'].get_mp_global_field_value('internal_categ')
            if mp_categ:
                vals["categ_id"] = mp_categ
            # custom
            if vals.get('public_categ_id', False):
                vals['public_categ_ids'] = [vals['public_categ_id']]
            # auto publish
            vals["website_published"] = True
            ###
        product_template = super(ProductTemplate, self).create(vals)
        # custom
        # auto approve
        product_template.auto_approve()
        ###
        return product_template

    # Action methods

    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            if record.marketplace_seller_id and record.status != 'approved' and not record.website_published:
                raise UserError(_("You cannot publish unapproved products."))
            record.website_published = not record.website_published

    def mp_action_view_sales(self):
        self.ensure_one()
        action = self.env.ref('odoo_marketplace.wk_seller_slae_order_line_action')
        product_ids = self.product_variant_ids.ids
        tree_view_id = self.env.ref('odoo_marketplace.wk_seller_product_order_line_tree_view')
        form_view_id = self.env.ref('odoo_marketplace.wk_seller_product_order_line_form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'binding_view_types': action.binding_view_types,
            'view_mode': action.view_mode,
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'target': action.target,
            'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('state', 'in', ['sale', 'done']), ('product_id.product_tmpl_id', '=', self.id)],
        }

    def pending_qty_stock_request(self):
        for rec in self:
            pending_stock = self.env["marketplace.stock"].search([('product_temp_id','=',rec.id),('state','=','requested')])
            return {
                'name':'Update Marketplace Product Quantity',
                'type':'ir.actions.act_window',
                'res_model':'marketplace.stock',
                'view_mode':'form',
                'binding_view_types':'form',
                'res_id' : pending_stock[0].id,
                'target':'current',
            }

    # Business methods

    def send_mail_to_seller(self, mail_templ_id):
        """ """
        if not mail_templ_id:
            return False
        template_obj = self.env['mail.template'].browse(mail_templ_id)
        template_obj.with_company(self.env.company).send_mail(self.id, True)

    def auto_approve(self):
        for obj in self:
            auto_product_approve = obj.marketplace_seller_id.get_seller_global_fields('auto_product_approve')
            if auto_product_approve:
                obj.write({"status": "pending"})
                obj.sudo().approved()
            else:
                obj.write({"status": "pending"})
        return True

    def check_state_send_mail(self):
        resConfig = self.env['res.config.settings']
        for obj in self.filtered(lambda o: o.status in ["approved", "rejected"]):
            # Notify to admin by admin when product approved/reject
            if resConfig.get_mp_global_field_value("enable_notify_admin_on_product_approve_reject"):
                temp_id = resConfig.get_mp_global_field_value("notify_admin_on_product_approve_reject_m_tmpl_id")
                if temp_id:
                    self.send_mail_to_seller(temp_id)
            # Notify to Seller by admin  when product approved/reject
            if resConfig.get_mp_global_field_value("enable_notify_seller_on_product_approve_reject"):
                temp_id = resConfig.get_mp_global_field_value("notify_seller_on_product_approve_reject_m_tmpl_id")
                if temp_id:
                    self.send_mail_to_seller(temp_id)

    def approved(self):
        for obj in self:
            if not obj.marketplace_seller_id:
                raise Warning(_("Marketplace seller id is not assign to this product."))
            # custom
            # skip checking seller state
            # if obj.marketplace_seller_id.state == "approved":
            obj.sudo().write({"status": "approved", "sale_ok": True})
            obj.check_state_send_mail()
            if not obj.is_initinal_qty_set:
                obj.set_initial_qty()
            # else:
            #     raise Warning(
            #         _("Marketplace seller of this product is not approved."))
            ###
        return True

    def reject(self):
        for product_obj in self:
            if product_obj.status in ("draft", "pending", "approved") and product_obj.marketplace_seller_id:
                product_obj.write({
                    "sale_ok": False,
                    "website_published": False,
                    "status": "rejected"
                })
                product_obj.check_state_send_mail()

    # Called in server action
    def approve_product(self):
        self.filtered(lambda o: o.status == "pending" and o.marketplace_seller_id).approved()

    # Called in server action
    def reject_product(self):
        self.filtered(lambda o: o.status in ("draft", "pending", "approved") and o.marketplace_seller_id).reject()

    def set_initial_qty(self):
        for template_obj in self:
            location_id = template_obj.marketplace_seller_id.get_seller_global_fields('location_id')
            if len(self) == 1:
                if template_obj.qty < 0:
                    raise Warning(_('Initial Quantity can not be negative'))
            if not location_id:
                raise Warning(_("Product seller has no location/warehouse."))
            if template_obj.qty > 0:
                vals = {
                    'product_id': template_obj.product_variant_ids[0].id,
                    'product_temp_id': template_obj.id,
                    'new_quantity': template_obj.qty,
                    'location_id': location_id or False,  # Phase 2
                    'note': _("Initial Quantity."),
                    'state': "requested",
                }
                mp_product_stock = self.env['marketplace.stock'].create(vals)
                template_obj.is_initinal_qty_set = True
                mp_product_stock.auto_approve()

    def disable_seller_all_products(self, seller_id):
        if seller_id:
            product_objs = self.search(
                [("marketplace_seller_id", "=", seller_id), ("status", "not in", ["draft", "rejected"])])
            product_objs.reject()

    def set_pending(self):
        for rec in self:
            rec.auto_approve()

    # custom
    def set_pending_partner(self):
        for rec in self:
            if rec.marketplace_seller_id: 
                rec.marketplace_seller_id.set_to_pending()
                return {
                    'name': 'Seller Profile',
                    'type': 'ir.actions.act_window',
                    'res_model': 'res.partner',
                    'view_mode': 'form',
                    'binding_view_types': 'form',
                    'res_id' : rec.marketplace_seller_id.id,
                    'view_id': self.env.ref('odoo_marketplace.wk_seller_form_view').id,
                    'context': { 'default_seller': 1, 'search_default_seller_status_filter': 1, 'no_archive': 1},
                    'target': 'current',
                }
    ### 

    def send_to_draft(self):
        for rec in self:
            rec.write({"status": "draft"})

    def write(self, vals):
        if vals.get("marketplace_seller_id", False):
            for rec in self:
                if rec.marketplace_seller_id and rec.status not in ["draft", "pending"]:
                    raise UserError(_('You cannot change the seller of the product that already contains seller.'))
        # custom
        if vals.get('public_categ_id'):
            vals['public_categ_ids'] = vals['public_categ_id'] and [vals['public_categ_id']] or []
        ###
        return super(ProductTemplate, self).write(vals)

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)

        if not self.env.context.get('website_sale_stock_get_quantity'):
            return combination_info

        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            seller_obj = product.marketplace_seller_id
            if seller_obj and seller_obj.seller:
                warehouse_id = seller_obj.get_seller_global_fields("warehouse_id")
                if warehouse_id:
                    product.with_context(warehouse=warehouse_id)._compute_quantities()
                    combination_info.update({
                        'virtual_available': product.virtual_available,
                    })
        return combination_info

    def get_marketplace_seller_id(self):
        if not self.marketplace_seller_id.id:
            return False
        return self.marketplace_seller_id.id


class ProductProduct(models.Model):
    _inherit = 'product.product'

    activity_date_deadline = fields.Date(
        'Next Activity Deadline', related='activity_ids.date_deadline',
        readonly=True, store=True,
        groups="base.group_user,odoo_marketplace.marketplace_seller_group")

    # Action methods

    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.product_tmpl_id.toggle_website_published()

    def mp_action_view_sales(self):
        self.ensure_one()
        action = self.env.ref('odoo_marketplace.wk_seller_slae_order_line_action')
        tree_view_id = self.env.ref('odoo_marketplace.wk_seller_product_order_line_tree_view')
        form_view_id = self.env.ref('odoo_marketplace.wk_seller_product_order_line_form_view')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'binding_view_types': action.binding_view_types,
            'view_mode': action.view_mode,
            'views': [(tree_view_id.id, 'tree'), (form_view_id.id, 'form')],
            'target': action.target,
            'context': "{'default_product_id': " + str(self.id) + "}",
            'res_model': action.res_model,
            'domain': [('state', 'in', ['sale', 'done']), ('product_id', '=', self.id)],
        }

    def pending_qty_stock_request(self):
        for rec in self:
            pending_stock = self.env["marketplace.stock"].search([('product_id','=',rec.id),('state','=','requested')])
            return {
                'name':'Update Marketplace Product Quantity',
                'type':'ir.actions.act_window',
                'res_model':'marketplace.stock',
                'view_mode':'form',
                'binding_view_types':'form',
                'res_id' : pending_stock[0].id,
                'target':'current',
            }

# custom
class ProductKeyword(models.Model):
    _name = 'product.keyword'
    _description = 'Product Keyword'
    _order = 'name'

    name = fields.Char('Name')


class EcommerceSearchHistory(models.Model):
    _name = 'ecommerce.search.history'
    _description = 'Ecommerce Search History'
    _order = 'create_date desc'

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', 'User')


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    project = fields.Boolean(string="Project")

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if not self.parent_id:
            self.project = False
        else:
            self.project = True if self.parent_id.project else False

    # custom
    def name_get(self):
        res = []
        for category in self:
            res.append((category.id, category.name))
        return res
    ###

class ProjectPortofolio(models.Model):
    _name = 'project.portofolio'
    _description = 'Project Portofolio'

    name = fields.Char('Name')
    description = fields.Text('Description')
    file_name = fields.Char(string='Document Name')
    file_upload = fields.Binary(string='Document File')
    project_id = fields.Many2one('product.template')
