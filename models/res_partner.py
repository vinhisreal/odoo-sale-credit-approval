from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(
        string="Credit Limit",
        help="Maximum credit allowed for this customer."
    )

    total_debt = fields.Float(
        string="Outstanding Debt",
        compute="_compute_total_debt",
        store=True,
        readonly=True
    )

    warning_message = fields.Char(
        string="Credit Warning Message",
        compute="_compute_warning_message",
        compute_sudo=True

    )

    # COMPUTE TOTAL DEBT
    @api.depends('invoice_ids.amount_residual', 'invoice_ids.payment_state')
    def _compute_total_debt(self):
        """Sum unpaid customer invoices SMART + performant"""

        AccountMove = self.env['account.move']

        # group all partner ids
        partner_ids = self.ids

        if not partner_ids:
            for partner in self:
                partner.total_debt = 0.0
            return

        # read_group = ONLY ONE SQL QUERY
        data = AccountMove.read_group(
            domain=[
                ('partner_id', 'in', partner_ids),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid'),
            ],
            fields=['amount_residual'],
            groupby=['partner_id'],
        )

        debt_map = {
            d['partner_id'][0]: d['amount_residual']
            for d in data
        }

        for partner in self:
            partner.total_debt = debt_map.get(partner.id, 0.0)

    # CREDIT CHECK
    def check_credit_limit(self, order_amount=0.0):
        for partner in self.sudo():
            if partner.credit_limit and (
                partner.total_debt + order_amount > partner.credit_limit
            ):
                raise ValidationError(
                    f"Customer {partner.name} would exceed their credit limit of "
                    f"{partner.credit_limit}.\n\n"
                    f"• Current debt: {partner.total_debt}\n"
                    f"• Order amount: {order_amount}\n"
                    f"• Total: {partner.total_debt + order_amount}"
                )
    @api.depends('total_debt', 'credit_limit')
    def _compute_warning_message(self):
        for partner in self:
            if (
                partner.credit_limit
                and partner.total_debt > partner.credit_limit
            ):
                partner.warning_message = (
                    f"Credit limit exceeded!\n"
                    f"Limit: {partner.credit_limit}\n"
                    f"Current debt: {partner.total_debt}"
                )
            else:
                partner.warning_message = False

    @api.model_create_multi
    def create(self, vals_list):
        # loop multiple creates
        for vals in vals_list:
            if 'credit_limit' in vals:
                if not self.env.user.has_group('account.group_account_manager') \
                   and not self.env.user.has_group('odoo_sale_credit_approval.group_sale_approver'):
                    raise AccessError("You are not allowed to set Credit Limit.")
        return super().create(vals_list)

    def write(self, vals):
        if 'credit_limit' in vals:
            if not self.env.user.has_group('account.group_account_manager') \
               and not self.env.user.has_group('odoo_sale_credit_approval.group_sale_approver'):
                raise AccessError("You are not allowed to modify Credit Limit.")
        return super().write(vals)