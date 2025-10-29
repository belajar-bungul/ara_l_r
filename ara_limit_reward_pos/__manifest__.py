# encoding: utf-8
{
    "name": "Limit Promotions by Points or Amount + Flash Sale Coupons – POS & Sales",
    "version": "18.0.0.0.1",
    "license": "OPL-1",
    "summary": "POS and Sale Customization",
    "category": "Sale",
    "author": "ARA SOFT",
    "website": "",
    "description": """
         Reward Use Type coupon and promotions
    """,
    "depends": ["point_of_sale", "sale_loyalty", "pos_loyalty", "base", "web", 'loyalty', 'sale'],
    "images": [],
    "init_xml": [],
    "data": [
        "security/ir.model.access.csv",
        "views/loyalty_program_views.xml",
    ],
    "assets": {
        'point_of_sale._assets_pos': [
            '/ara_limit_reward_pos/static/src/js/OrderScreen.js',
        ]
    },
    "installable": True,
    "price" : 60.10,
    "currency": "USD",
    "images": ['static/description/banner.gif'],

}
