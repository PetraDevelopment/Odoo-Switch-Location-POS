
import logging
from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero
_logger = logging.getLogger(__name__)


class location(models.Model):
    _inherit = "stock.move.line"
    
    pos_session_id = fields.Many2one('pos.session', string='POS Session')
    # @api.returns('stock.warehouse', lambda value: value.id)
    # def get_warehouse(self):
    #     """ Returns warehouse id of warehouse that contains location """
    #     domain = [('view_location_id', 'parent_of', self.ids)]
    #     return self.env['stock.warehouse'].search(domain, limit=1)
