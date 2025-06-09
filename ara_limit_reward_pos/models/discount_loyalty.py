from odoo import models, fields, api, _
from collections import defaultdict
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from uuid import uuid4
import pytz
from datetime import datetime


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    limit_value_program = fields.Float(
        string="Limit Value", help="Limit value for the loyalty program", copy=False)

    value_used_program = fields.Float(
        string="Value Used", help="Value used for the loyalty program", copy=False)

    date_start_flash_sale = fields.Datetime(
        "Start Date Flash Sale", copy=False)

    date_end_flash_sale = fields.Datetime("End Date Flash Sale", copy=False)

    # OVERRIDE
    @api.model
    def _load_pos_data_fields(self, config_id):
        return [
            'name', 'trigger', 'applies_on', 'program_type', 'pricelist_ids', 'date_from',
            'date_to', 'limit_usage', 'max_usage', 'is_nominative', 'portal_visible',
            'portal_point_name', 'trigger_product_ids', 'rule_ids', 'reward_ids', 'value_used_program',
            'limit_value_program', 'date_start_flash_sale', 'date_end_flash_sale'
        ]

    def get_program(self, id):
        localize_time = pytz.timezone(self.env.user.tz or 'UTC')
        search_val = self.search([('id', '=', id)], limit=1)

        localize_time_tz_start = ''
        localize_time_tz_end = ''

        if search_val.date_start_flash_sale:
            localize_time_tz_start = pytz.utc.localize(search_val.date_start_flash_sale)\
                .astimezone(localize_time).strftime('%Y-%m-%d %H:%M:%S')

        if search_val.date_end_flash_sale:
            localize_time_tz_end = pytz.utc.localize(search_val.date_end_flash_sale)\
                .astimezone(localize_time).strftime('%Y-%m-%d %H:%M:%S')

        today = datetime.utcnow()
        today_eks = pytz.utc.localize(today).astimezone(
            localize_time).strftime('%Y-%m-%d %H:%M:%S')

        if search_val:
            return {
                'name': search_val.name,
                'limit_value_program': search_val.limit_value_program,
                'value_used_program': search_val.value_used_program,
                'date_start_flash_sale': localize_time_tz_start,
                'date_end_flash_sale': localize_time_tz_end,
                'today': today_eks,
            }
        return False

    def get_program_promos(self, id):
        search_val = self.search([('id', '=', id),
                                 ('program_type', '=', 'promotion')], limit=1)

        if search_val:
            return {
                'name': search_val.name,
                'limit_value_program': search_val.limit_value_program,
                'value_used_program': search_val.value_used_program,
            }
        return False

    use_limit_ids = fields.One2many('use.limit.program', 'program_id')


class UseLimitProgram(models.Model):
    _name = "use.limit.program"

    program_id = fields.Many2one(
        'loyalty.program',
        string='program',
    )
    name = fields.Char("Source")
    value_use = fields.Monetary(
        string="Value Use",
        res_currency="currency_id",
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id'
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
