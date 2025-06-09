/** @odoo-module */
import { PosStore } from "@point_of_sale/app/store/pos_store"
import { patch } from "@web/core/utils/patch"
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog"
const { DateTime } = luxon

patch(PosStore.prototype, {
    async updateRewards() {
        const currentOrder = this.get_order()
        const orderlines = currentOrder.get_orderlines()

        if (!this.env.services.pos_data.network.offline) {
            for (const line of orderlines) {
                const reward = line.reward_id

                if (reward) {
                    const search_program_result = await this.data.orm.call(
                        "loyalty.program",
                        "get_program",
                        [[1], reward.program_id.id]
                    )

                    if (reward.program_id.program_type === "coupons") {
                        const {
                            date_start_flash_sale,
                            date_end_flash_sale,
                            today,
                        } = search_program_result

                        if (
                            date_start_flash_sale &&
                            date_end_flash_sale &&
                            today
                        ) {
                            const todayDate = new Date(today)
                            const startDate = new Date(date_start_flash_sale)
                            const endDate = new Date(date_end_flash_sale)

                            if (
                                isNaN(todayDate) ||
                                isNaN(startDate) ||
                                isNaN(endDate)
                            ) {
                                console.warn(
                                    "[POS WARNING] Invalid flash sale dates received",
                                    search_program_result
                                )
                                return super.updateRewards()
                            }

                            if (todayDate > endDate) {
                                this.dialog.add(AlertDialog, {
                                    title: "Notif",
                                    body: `Program is End`,
                                })
                                currentOrder.removeOrderline(line)
                                return this.resetPrograms()
                            }

                            if (todayDate < startDate) {
                                this.dialog.add(AlertDialog, {
                                    title: "Notif",
                                    body: `Program `,
                                })
                                currentOrder.removeOrderline(line)
                                return this.resetPrograms()
                            }

                            return super.updateRewards()
                        } else {
                            console.warn(
                                "[POS WARNING] Flash sale dates missing",
                                search_program_result
                            )
                            return super.updateRewards()
                        }
                    }
                }
            }
        }

        return super.updateRewards()
    },
    async pay() {
        const currentOrder = this.get_order()
        const orderlines = currentOrder.get_orderlines()
        if (!this.env.services.pos_data.network.offline) {
            for (const line of orderlines) {
                const reward = line.reward_id
                if (reward) {
                    const search_program_result = await this.data.orm.call(
                        "loyalty.program",
                        "get_program",
                        [[1], reward.program_id.id]
                    )
                    const program = search_program_result
                    const limitValue = program.limit_value_program || 0
                    const valueUsed = program.value_used_program || 0
                    const priceUnit = Math.abs(line.price_unit) || 0
                    const totalValue = valueUsed + priceUnit
                    if (totalValue >= limitValue) {
                        this.dialog.add(AlertDialog, {
                            title: "Promo Limit Reached",
                            body: `The promotion '${program.name}' has reached its usage limit. This promotional item or discount will be removed from the order.`,
                        })
                        currentOrder.removeOrderline(line)

                        return
                    }
                }
            }
        } else {
            for (const line of orderlines) {
                const reward = line.reward_id
                console.log("[POS DEBUG] Memeriksa orderline:", line)
                if (reward) {
                    currentOrder.removeOrderline(line)
                    this.dialog.add(AlertDialog, {
                        title: "Notification",
                        body: `The POS is currently offline. The order total has changed because the promotional discount could not be applied.`,
                    })
                }
            }
            return super.pay()
        }
        return super.pay()
    },
})
