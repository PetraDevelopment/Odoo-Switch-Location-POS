
import logging
from odoo import models
_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    """The class PosSession is used to inherit pos.session"""

    _inherit = 'pos.session'

    def load_pos_data(self):
        """Load POS data and add `res_users` to the response dictionary.
        return: A dictionary containing the POS data.
        """
        res = super(PosSession, self).load_pos_data()
        # Add domain filter to search only for internal locations
        domain = [('usage', '=', 'internal')]
        # Specify the fields to include in the search result
        fields = ['name', 'location_id']
        locations = self.env['stock.location'].search_read(domain, fields)
        _logger.info("Locations found: %s", locations)
        res['locations'] = locations
        return res

    def _create_picking_at_end_of_session(self):
        self.ensure_one()
        if not self.config_id.switch_stock_location:
            return super(PosSession, self)._create_picking_at_end_of_session()

        lines_grouped_by_dest_location = {}

        # Default session destination
        session_destination_id = self.env['stock.warehouse']._get_partner_locations()[
            0].id

        for order in self.order_ids:
            if order.company_id.anglo_saxon_accounting and (order.is_invoiced or order.to_ship):
                continue
            for line in order.lines:
                location_id = line.location_id_from_popup.id if line.location_id_from_popup else None

                if location_id:
                    location = self.env['stock.location'].browse(location_id)
                    warehouse = location.get_warehouse()
                    _logger.info("location found for line ?  %s", location)
                    _logger.info("warehouse found for line ?  %s", warehouse)
                    print("warehouse id ", warehouse.id)

                    if warehouse:
                        picking_types = self.env['stock.picking.type'].search([
                            ('warehouse_id.id', '=', warehouse.id),
                            ('code', '=', 'outgoing')
                        ])
                        picking_type = picking_types[1] if len(
                            picking_types) > 1 else picking_types[0]

                        if picking_type and picking_type.default_location_dest_id:
                            session_destination_id = picking_type.default_location_dest_id.id

                        destination_id = order.partner_id.property_stock_customer.id or session_destination_id
                        key = (destination_id, picking_type, location_id)

                        if key in lines_grouped_by_dest_location:
                            lines_grouped_by_dest_location[key] |= line
                        else:
                            lines_grouped_by_dest_location[key] = line
                    else:
                        _logger.info(
                            "No warehouse found for location %s", location_id)
                else:
                    _logger.info("No location_id found for line %s", line)
                    picking_type = order.config_id.picking_type_id
                    if not picking_type or not picking_type.default_location_dest_id:
                        session_destination_id = self.env['stock.warehouse']._get_partner_locations()[
                            0].id
                    else:
                        session_destination_id = picking_type.default_location_dest_id.id
                    destination_id = order.partner_id.property_stock_customer.id or session_destination_id
                    key = (destination_id, picking_type, location_id)

                    if key in lines_grouped_by_dest_location:
                        lines_grouped_by_dest_location[key] |= line
                    else:
                        lines_grouped_by_dest_location[key] = line

        for (location_dest_id, picking_type, location_id), lines in lines_grouped_by_dest_location.items():
            _logger.info("closed machines location_id in var %s", location_id)
            _logger.info("closed machines lines_grouped_by_dest_location.items() %s",
                         lines_grouped_by_dest_location.items())
            _logger.info(
                "closed machines picking_type in var %s", picking_type)
            pos_session_id = self
            print("pos_session_id in _create_picking_at_end_of_session ",
                  pos_session_id)
            _logger.info(
                "Creating pickings at the end of session for line in lines location_id %s", location_id)

            pickings = self.env['stock.picking']._create_picking_from_pos_order_lines(
                location_dest_id, lines, picking_type, order.partner_id, location_id=location_id, pos_session_id=pos_session_id
            )
            pickings.write({'pos_session_id': self.id, 'origin': self.name})

        return True
