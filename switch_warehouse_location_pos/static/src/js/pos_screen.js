/** @odoo-module **/
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";

export class SetProductListButton extends Component {
  setup() {
    super.setup();
    this.pos = usePos();
    const { popup } = this.env.services;
    this.popup = popup;
  }

  get productsList() {
    let list = [];
    list = this.pos.db.get_product_by_category(this.pos.selectedCategoryId);
    return list.sort(function (a, b) {
      return a.display_name.localeCompare(b.display_name);
    });
  }

  async onClick() {
    let list = this.productsList;

    // Check if selectedOrder and selected_orderline exist
    if (!this.pos.selectedOrder) {
      console.error("No selected order found.");
      return;
    }

    if (!this.pos.selectedOrder.selected_orderline) {
      console.error("No selected orderline found.");
      return;
    }

    // Location selection
    const locationList = this.pos.locations.map((location) => {
      return {
        id: location.id,
        item: location,
        label: location.name + " (" + location.location_id[1] + ")",
        isSelected: false,
      };
    });
    const { confirmed: locationConfirmed, payload: location } =
      await this.popup.add(SelectionPopup, {
        title: _t("Select the Location"),
        list: locationList,
      });

    if (locationConfirmed) {
      this.pos.selectedOrder.selected_orderline.location_string =
        location.name + " (" + location.location_id[1] + ")";
      this.pos.selectedOrder.selected_orderline.location_id_from_popup =
        location.id;
    }
  }
}

SetProductListButton.template = "SalesPersonButton";
ProductScreen.addControlButton({
  component: SetProductListButton,
  condition: function () {
    return this.pos.config.switch_stock_location;
  },
});
