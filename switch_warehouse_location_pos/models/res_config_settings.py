from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_switch_stock_location = fields.Boolean(related="pos_config_id.switch_stock_location",
                                              string="Switch Stock Location", help="Allow switching stock locations for products.", readonly=False)
   