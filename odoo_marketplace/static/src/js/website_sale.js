odoo.define('odoo_marketplace.website_sale_shop', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var VariantMixin = require('sale.VariantMixin');
    // var WebsiteSale = require('website_sale.WebsiteSale');

    publicWidget.registry.WebsiteSaleShop = publicWidget.Widget.extend(VariantMixin, {
        selector: '.oe_website_sale',
        events: _.extend({}, VariantMixin.events || {}, {
            'submit .o_wsale_products_searchbar_form_custom': '_onSubmitSaleSearchProducts',
        }),
        /**
         * @constructor
         */
        init: function () {
            console.log('Init');
            var self = this;
            var def = this._super.apply(this, arguments);
            return def;
        },
        /**
         * @override
         */
        start: function () {
            console.log('start');
            var self = this;
            var def = this._super.apply(this, arguments);
            return def;
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onSubmitSaleSearchProducts: function (ev) {
            console.log('custom');
            if (!this.$('.dropdown_sorty_by').length) {
                return;
            }
            var $this = $(ev.currentTarget);
            if (!ev.isDefaultPrevented() && !$this.is(".disabled")) {
                ev.preventDefault();
                var oldurl = $this.attr('action');
                oldurl += (oldurl.indexOf("?")===-1) ? "?" : "";
                var search = $this.find('input.search-query');
                var searchState = $this.find('select.search-query-state');
                var searchSubCategory = $this.find('select.search-query-sub-categ');
                var redirectUrl = oldurl
                if (searchSubCategory && oldurl.includes('/category/')) {
                    var pref_url = oldurl.split('/category/')[0]
                    var new_url = pref_url
                    console.log(encodeURIComponent(searchSubCategory.val()));
                    if (encodeURIComponent(searchSubCategory.val()) !== '0') {
                        new_url += '/category/' + encodeURIComponent(searchSubCategory.val()) + '?category=' + encodeURIComponent(searchSubCategory.val());
                    }
                    redirectUrl = new_url;
                }
                if (search) {
                    redirectUrl += '&' + search.attr('name') + '=' + encodeURIComponent(search.val());
                }
                if (searchState) {
                    redirectUrl += '&' + searchState.attr('name') + '=' + encodeURIComponent(searchState.val());
                }
                window.location = redirectUrl;
            }
        },
    });
});