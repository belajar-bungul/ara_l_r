from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
import pytz
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        self.order_line._trigger_limit_use_program()
        return super().action_confirm()

    def _action_cancel(self):
        self.order_line._trigger_remove_use_program()
        return super()._action_cancel()

    def action_open_reward_wizard(self):
        self.ensure_one()
        self._update_programs_and_rewards()
        claimable_rewards = self._get_claimable_rewards()
        if len(claimable_rewards) == 1:
            coupon = next(iter(claimable_rewards))
            rewards = claimable_rewards[coupon]
            if len(rewards) == 1 and not rewards.multi_product:
                self._apply_program_reward(claimable_rewards[coupon], coupon)
                self.order_line._check_loyalty_limit()  # override
                return True
        elif not claimable_rewards:
            return True
        return self.env['ir.actions.actions']._for_xml_id('sale_loyalty.sale_loyalty_reward_wizard_action')


class SaleLoyaltyRewardWizard(models.TransientModel):
    _inherit = 'sale.loyalty.reward.wizard'

    def action_apply(self):
        res = super().action_apply()
        self.order_id.order_line._check_loyalty_limit()  # override
        return res
