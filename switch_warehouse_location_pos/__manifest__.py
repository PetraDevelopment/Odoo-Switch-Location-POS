{
    'name': 'Switch Between Warehouses in POS',
   
    'Version': '17.0.1.0.0',
    'summary': 'This module is used to set location  on pos order line',
    'description': 'This module allows you to assign location to order'
                   'lines in the Point of Sale (POS) Switch Between Warehouses in POS 17 Development',
  

    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/pos_orderline_views.xml',
        # 'views/stock_move_line.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'switch_warehouse_location_pos/static/src/js/pos_load_data.js',
            'switch_warehouse_location_pos/static/src/js/pos_screen.js',
            'switch_warehouse_location_pos/static/src/js/orderline.js',
            'switch_warehouse_location_pos/static/src/js/pos_orderline.js',
            'switch_warehouse_location_pos/static/src/xml/pos_screen_templates.xml',
            'switch_warehouse_location_pos/static/src/xml/orderline_templates.xml',
        ],
    },

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
     'website': 'www.t-petra.com',
    'author':'Petra Software',
    'company': 'Petra Software',
    'maintainer': 'Petra Software',
    'images': ['static/description/banner.png'],
        'price':30,
      'currency':'USD',
}
