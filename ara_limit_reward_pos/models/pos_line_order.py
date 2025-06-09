from odoo import models, fields, api, _

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create(self, values):
        result = super().create(values)
        result.lines._prepare_calculate_used_reward()
        return result

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    def _trigger_limit_use_program(self):
        if not self.order_id.refunded_order_id:
            for val in self.filtered(lambda r: r.reward_id and r.reward_id.program_id):
                program = val.reward_id.program_id
                if program.program_type in ('coupons', 'promotion'):
                    self.env['use.limit.program'].sudo().create({
                        'name': val.order_id.name,
                        'value_use': abs(val.price_subtotal_incl or 0.0),
                        'program_id': program.id,
                    })

    def _trigger_remove_use_program(self):
        for val in self.filtered(lambda r: r.reward_id and r.reward_id.program_id):
            program = val.reward_id.program_id
            if program.program_type in ('coupons', 'promotion'):
                data_set = self.env['use.limit.program'].search(
                    [('name', '=', val.order_id.name)])
                total_to_remove = sum(data.value_use for data in data_set)
                program.sudo().write({
                    'value_used_program': program.value_used_program - total_to_remove,
                })
                for data in data_set:
                    data.sudo().unlink()

    def _prepare_calculate_used_reward(self):
        for val in self.filtered(lambda r: r.reward_id and r.reward_id.program_id):
            program = val.reward_id.program_id
            if program.pos_ok and program:
                disc_val = abs(val.price_subtotal_incl)
                total_discount = program.value_used_program + disc_val
                if total_discount >= program.limit_value_program:
                    program.write({
                        'pos_ok': False,
                        'sale_ok': False
                    })
                else:
                    program.write({
                        'value_used_program': total_discount
                    })
                    program.write({
                        'pos_ok': True,
                        'sale_ok': True
                    })
                    self._trigger_limit_use_program()
