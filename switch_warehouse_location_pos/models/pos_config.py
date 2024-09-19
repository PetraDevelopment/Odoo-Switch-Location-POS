import logging
from odoo import api, fields, models
from odoo.fields import Command
from odoo.tools.float_utils import float_is_zero
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    """Inherited model for adding new field to configuration settings
                that allows to switch stock from pos session"""
    _inherit = 'pos.config'

    switch_stock_location = fields.Boolean(
        "Switch Stock Location", help="Allow switching stock locations for products.")

