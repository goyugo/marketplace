odoo.define('pn_portal_customer.portal', function (require) {
    "use strict";

    require('portal.portal');
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.portalDetails = publicWidget.Widget.extend({
        selector: '.o_portal_details',
        events: {
            'change select[name="country_id"]': '_onCountryChange',
        },

        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);

            this.$state = this.$('select[name="state_id"]');
            this.$stateOptions = this.$state.filter(':enabled').find('option:not(:first)');
            this._adaptAddressForm();

            return def;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _adaptAddressForm: function () {
            var $country = this.$('select[name="country_id"]');
            var countryID = ($country.val() || 0);
            this.$stateOptions.detach();
            var $displayedState = this.$stateOptions.filter('[data-country_id=' + countryID + ']');
            var nb = $displayedState.appendTo(this.$state).show().length;
            this.$state.parent().toggle(nb >= 1);

            var phone_code = $("span[name='phone_code']");
            var $country = this.$('select[name="country_id"]');
            var countryID = ($country.val() || 0);
            rpc.query({
                model: 'res.country',
                method: 'get_phone_code',
                args: [parseInt(countryID)],
            }).then(function (result) {
                phone_code[0]['innerText'] = '+' + result
            })
        },

        /**
         * @private
         */
        _onCountryChange: function () {
            this._adaptAddressForm();
        },
    });
})