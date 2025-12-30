from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    requires_approval = fields.Boolean(
        string="Requires Approval",
        default=False,
        readonly=True
    )

    approved = fields.Boolean(
        string="Approved",
        default=False,
        readonly=True
    )

    approval_threshold = fields.Float(
        string="Approval Threshold",
        default=20000000,
        help="Order amount above which approval is required."
    )

    # RESET APPROVAL IF ORDER CHANGED
    @api.onchange('order_line')
    def _onchange_order_line_reset_approval(self):
        if self.approved:
            self.approved = False
            self.requires_approval = False

    # APPROVE BUTTON (MANAGER ONLY)
    def action_approve_order(self):
        self.ensure_one()

        if not self.env.user.has_group(
            'odoo_sale_credit_approval.group_sale_approver'
        ):
            raise ValidationError("You do not have rights to approve orders.")

        self.write({
            'approved': True,
            'requires_approval': False
        })

        self.message_post(
            body=f"Order approved by {self.env.user.name}"
        )


    # CONFIRM ORDER WITH CREDIT CHECK
    def action_confirm(self):
        approver = self.env.user.has_group(
            'odoo_sale_credit_approval.group_sale_approver'
        )

        orders_to_check = self.filtered(lambda o: o.state in ('draft', 'sent'))

        for order in orders_to_check:

            # CREDIT LIMIT CHECK 
            if order.partner_id and order.partner_id.credit_limit:
                order.partner_id.check_credit_limit(order.amount_total)

            # APPROVAL LOGIC
            if order.amount_total >= order.approval_threshold:

                if not order.approved:
                    order.requires_approval = True
                    raise ValidationError(
                        "This order exceeds the approval threshold.\n"
                        "It must be approved before confirmation."
                    )


        return super().action_confirm()
