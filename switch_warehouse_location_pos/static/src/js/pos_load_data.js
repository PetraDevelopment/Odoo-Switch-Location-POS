/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
  async _processData(loadedData) {
    await super._processData(...arguments);

    this.locations = loadedData["locations"]; // Load locations
    console.log(
      "POS data processed: res_users and locations loaded.",

      this.locations
    );
  },
});
