/**@odoo-module **/
import AbstractAwaitablePopup from "point_of_sale.AbstractAwaitablePopup";
import Registries from "point_of_sale.Registries";
const { useRef } = owl;
var core = require("web.core");
const { Gui } = require("point_of_sale.Gui");
var _t = core._t;

class SalesPersonPopup extends AbstractAwaitablePopup {
  setup() {
    super.setup();
    this.locationRef = useRef("locationRef");
    console.log("SalesPersonPopup setup completed", this.locationRef);
    console.log("Props locations:", this.props.locations);
    console.log("Props location_id:", this.props.location_id);
  }

  confirm() {
    try {
      if (this.env.pos.config.switch_stock_location) {
        if (this.env.pos.selectedOrder.selected_orderline) {
          let locationOption = this.locationRef.el.selectedOptions[0];
          console.log("Selected location option:", locationOption);
          this.env.pos.selectedOrder.selected_orderline.location = [
            parseInt(locationOption.id),
            locationOption.textContent.trim(),
          ];
          console.log(
            "Orderline updated with location:",
            this.env.pos.selectedOrder.selected_orderline
          );
          console.log(
            "Selected location option locationOption:",
            locationOption.value
          );
          console.log(
            "Selected location option `slot{locationOption.value :",
            `slot"${locationOption.value}"${
              locationOption.id
            }"${locationOption.textContent.trim()}"`
          );

          this.env.posbus.trigger("close-popup", {
            popupId: this.props.id,
            response: {
              confirmed: true,
              payload: null,
            },
          });
        }
      } else {
        Gui.showPopup("ErrorPopup", {
          title: _t("Error"),
          body: _t("You should add product first"),
        });
        console.error("Error: No selected orderline found");
        return false;
      }
    } catch (error) {
      console.error("Error in confirm method:", error);
    }
  }

  cancel() {
    try {
      this.env.posbus.trigger("close-popup", {
        popupId: this.props.id,
        response: {
          confirmed: false,
          payload: null,
        },
      });
      console.log("Popup cancelled");
    } catch (error) {
      console.error("Error in cancel method:", error);
    }
  }
}

SalesPersonPopup.template = "SalesPersonPopup";
Registries.Component.add(SalesPersonPopup);

export default SalesPersonPopup;
