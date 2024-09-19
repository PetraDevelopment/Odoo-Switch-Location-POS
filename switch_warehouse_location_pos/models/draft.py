
from odoo import api, fields, models


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

from itertools import groupby
from collections import defaultdict
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _create_order_picking(self):
        self.ensure_one()
        if not self.config_id.switch_stock_location:
            return super(PosOrder, self)._create_order_picking()

        locations_from_popup = self.lines.mapped(
            'location_id_from_popup').filtered(lambda l: l)

        if self.to_ship:
            self.lines._launch_stock_rule_from_pos_order_lines()
        else:
            if self._should_create_picking_real_time():

                pickings = self.env['stock.picking']

                for location_id_from_popup in locations_from_popup:
                    location_id = location_id_from_popup.id
                    lines_with_location = self.lines.filtered(
                        lambda l: l.location_id_from_popup.id == location_id)

                    location = self.env['stock.location'].browse(
                        location_id)

                    # Find warehouse associated with this location
                    warehouse_filter = location.get_warehouse()

                    if warehouse_filter:
                        picking_types = self.env['stock.picking.type'].search([
                            ('warehouse_id.id', '=', warehouse_filter.id),
                            ('code', '=', 'outgoing')
                        ])
                        if picking_types:
                            picking_type = picking_types[1] if len(
                                picking_types) > 1 else picking_types[0]
                        else:
                            # Updated: Ensure picking_type is assigned a value
                            picking_type = self.config_id.picking_type_id
                    else:
                        # Updated: Ensure picking_type is assigned a value
                        picking_type = self.config_id.picking_type_id

                    if self.partner_id.property_stock_customer:
                        destination_id = self.partner_id.property_stock_customer.id
                    elif not picking_type or not picking_type.default_location_dest_id:
                        destination_id = self.env['stock.warehouse']._get_partner_locations()[
                            0].id
                    else:
                        destination_id = picking_type.default_location_dest_id.id

                    # Create picking for each location-specific line
                    picking = self.env['stock.picking']._create_picking_from_pos_order_lines(
                        destination_id, lines_with_location, picking_type, self.partner_id, location_id
                    )

                    picking.write({
                        'pos_session_id': self.session_id.id,
                        'pos_order_id': self.id,
                        'origin': self.name
                    })

                    pickings |= picking

                # Handle lines without specific popup locations
                lines_without_location = self.lines - \
                    self.lines.filtered(lambda l: l.location_id_from_popup)
                if lines_without_location:
                    picking_type = self.config_id.picking_type_id

                    if self.partner_id.property_stock_customer:
                        destination_id = self.partner_id.property_stock_customer.id
                    elif not picking_type or not picking_type.default_location_dest_id:
                        destination_id = self.env['stock.warehouse']._get_partner_locations()[
                            0].id
                    else:
                        destination_id = picking_type.default_location_dest_id.id
                    picking = self.env['stock.picking']._create_picking_from_pos_order_lines(
                        destination_id, lines_without_location, picking_type, self.partner_id
                    )

                    picking.write({
                        'pos_session_id': self.session_id.id,
                        'pos_order_id': self.id,
                        'origin': self.name
                    })

                    pickings |= picking

                return pickings


class PosOrderline(models.Model):
    """ The class PosOrder is used to inherit pos.order.line """

    _inherit = 'pos.order.line'
    user_id = fields.Many2one('res.users',
                              )

    location_id_from_popup = fields.Many2one(
        'stock.location', string='Location', domain="[('usage', 'in', ['internal', 'transit'])]", compute='_compute_location_from_popup', store=True)
    # check_value_of_swich = fields.Boolean()

    @api.depends('order_id', 'order_id.config_id.picking_type_id')
    def _compute_location_from_popup(self):
        for line in self:
            if not line.location_id_from_popup:
                line.location_id_from_popup = line.order_id.config_id.picking_type_id.default_location_src_id

    # def _defaultcheck_value_of_swich(self):
    #     # get the  instance. note that `company_id` is used in the search
    #     # domain to ensure the correct record is returned in multi-company environments
    #     # if the model is not multi-company-aware, you can use a blank domain
    #     print("in _defaultcheck_value_of_swich ")
    #     return self.env['pos.config'].search([('company_id', '=', self.env.company.id)], limit=1)

    # config_id = fields.Many2one(
    #     comodel_name='pos.config', default=_defaultcheck_value_of_swich)

    # check_value_of_switch = fields.Boolean(
    #     related='config_id.switch_stock_location')
    # make sure a reference to the  is available


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pos_session_id = fields.Many2one('pos.session', index=True)
    pos_order_id = fields.Many2one('pos.order', index=True)

    @api.model
    def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False, location_id=None):
        pickings = self.env['stock.picking']
        stockable_lines = lines.filtered(lambda l: l.product_id.type in [
                                         'product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding))
        if not stockable_lines:
            return pickings
        positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
        negative_lines = stockable_lines - positive_lines

        if positive_lines:
            location_id = location_id or picking_type.default_location_src_id.id
            positive_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(
                    partner, picking_type, location_id, location_dest_id)
            )
            positive_picking._create_move_from_pos_order_lines(positive_lines)
            self.env.flush_all()
            try:
                with self.env.cr.savepoint():
                    positive_picking._action_done()
            except (UserError, ValidationError):
                pass

            pickings |= positive_picking
        if negative_lines:
            if picking_type.return_picking_type_id:
                return_picking_type = picking_type.return_picking_type_id
                return_location_id = return_picking_type.default_location_dest_id.id
            else:
                return_picking_type = picking_type
                return_location_id = picking_type.default_location_src_id.id

            negative_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(
                    partner, return_picking_type, location_dest_id, return_location_id)
            )
            negative_picking._create_move_from_pos_order_lines(negative_lines)
            self.env.flush_all()
            try:
                with self.env.cr.savepoint():
                    negative_picking._action_done()
            except (UserError, ValidationError):
                pass
            pickings |= negative_picking
        return pickings


class location(models.Model):
    _inherit = "stock.location"

    @api.returns('stock.warehouse', lambda value: value.id)
    def get_warehouse(self):
        """ Returns warehouse id of warehouse that contains location """
        domain = [('view_location_id', 'parent_of', self.ids)]
        return self.env['stock.warehouse'].search(domain, limit=1)
