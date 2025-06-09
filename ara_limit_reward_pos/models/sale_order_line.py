from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
import pytz
from datetime import datetime


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _trigger_limit_use_program(self):
        for line in self:
            if not line.is_reward_line or not line.reward_id:
                continue
            program = line.reward_id.program_id
            if program.program_type in ('coupons', 'promotion'):
                self.env['use.limit.program'].sudo().create({
                    'name': line.order_id.name,
                    'value_use': abs(line.price_total or 0.0),
                    'program_id': program.id,
                })
                program.value_used_program += abs(line.price_total or 0.0)

    def _trigger_remove_use_program(self):
        for line in self:
            if not line.is_reward_line or not line.reward_id:
                continue
            program = line.reward_id.program_id
            if program.program_type in ('coupons', 'promotion'):
                data_set = self.env['use.limit.program'].search(
                    [('name', '=', line.order_id.name)])
                total_to_remove = sum(data.value_use for data in data_set)
                program.sudo().write({
                    'value_used_program': program.value_used_program - total_to_remove,
                })

                for data in data_set:
                    data.sudo().unlink()

    def _check_loyalty_limit(self):
        for line in self:
            if not line.is_reward_line or not line.reward_id:
                continue
            program = line.reward_id.program_id
            if program.program_type in ('coupons') and program.date_start_flash_sale and program.date_end_flash_sale:
                localize_time = pytz.timezone(self.env.user.tz or 'UTC')
                localize_time_tz_start = pytz.utc.localize(program.date_start_flash_sale)\
                    .astimezone(localize_time).strftime('%Y-%m-%d %H:%M:%S')
                localize_time_tz_end = pytz.utc.localize(program.date_end_flash_sale)\
                    .astimezone(localize_time).strftime('%Y-%m-%d %H:%M:%S')
                start_date = localize_time_tz_start
                end_date = localize_time_tz_end
                today = datetime.utcnow()
                today_tz = pytz.utc.localize(today).astimezone(
                    localize_time).strftime('%Y-%m-%d %H:%M:%S')
                if today_tz < start_date:
                    raise ValidationError(_(
                        "Coupon no active because start date '%s'",
                        start_date
                    ))
                if today_tz > end_date:
                    raise ValidationError(_(
                        "Coupon no active because end date '%s'",
                        end_date
                    ))
            if program.limit_value_program != 0 and program.program_type in ('coupons', 'promotion'):
                if program.program_type in ('coupons') and not program.date_start_flash_sale and not program.date_end_flash_sale:
                    raise ValidationError(_(
                        "Please your setup start and end date flash sale program coupons !"
                    ))
                else:
                    used = program.value_used_program or 0.0
                    attempted = abs(line.price_total or 0.0)
                    if used + attempted > program.limit_value_program:
                        raise ValidationError(_(
                            "Loyalty limit exceeded for program '%s'.\n"
                            "Limit: %.2f | Used: %.2f | Attempted: %.2f",
                            program.display_name,
                            program.limit_value_program,
                            used,
                            attempted,
                        ))
