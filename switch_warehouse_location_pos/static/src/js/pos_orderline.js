/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/store/models";

// Patching Orderline to add location functionality
patch(Orderline.prototype, {
  setup(_defaultObj, options) {
    super.setup(...arguments);
    if (options.json) {
      this.location_string = options.json.location_string;
      this.location_id_from_popup = options.json.location_id_from_popup;
    }
  },
  export_as_JSON() {
    var json = super.export_as_JSON.call(this);
    json.location_string = this.location_string || false;
    json.location_id_from_popup = this.location_id_from_popup || false;
    return json;
  },
  init_from_JSON(json) {
    super.init_from_JSON(...arguments);
    this.location_string = json.location_string;
    this.location_id_from_popup = json.location_id_from_popup;
  },
  get_location() {
    return {
      location_string: this.location_string,
      location_id_from_popup: this.location_id_from_popup,
    };
  },
  getDisplayData() {
    return {
      ...super.getDisplayData(),
      location_string: this.location_string,
      location_id_from_popup: this.location_id_from_popup,
    };
  },
});
