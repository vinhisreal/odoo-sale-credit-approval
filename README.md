# Sale Credit Limit & Approval (Odoo Module)

## Overview
This module implements **credit limit control** and an **approval workflow** for Sales Orders in Odoo.  
It prevents users from confirming Sales Orders that exceed a customer's credit limit or a predefined approval threshold without proper authorization.

The module is designed as a **business control feature** commonly required in real-world ERP systems.

---

## Key Features

### 1. Customer Credit Management
- Add **Credit Limit** to customers (`res.partner`)
- Automatically compute **Outstanding Debt** from unpaid customer invoices
- Efficient computation using `read_group` for performance

### 2. Credit Limit Enforcement
- Prevents Sales Order confirmation if:
```bash
    Current Debt + Order Amount > Credit Limit
```
- Displays a clear validation message explaining:
- Credit limit
- Current debt
- Order amount
- Total exposure

### 3. Approval Workflow for Large Orders
- Sales Orders exceeding the **Approval Threshold** require approval
- Introduces a custom user group: **Sales Order Approver**
- Only approvers can approve orders and allow confirmation
- Approval status is reset automatically if order lines are modified

### 4. Security & Access Control
- Only authorized users can:
- Set or modify customer credit limits
- Approve large Sales Orders
- Uses Odoo group-based access control (no hardcoded users)

---

## Workflow

1. **Sales User**
 - Creates a Sales Order
 - Attempts to confirm the order

2. **System Checks**
 - Credit limit validation
 - Approval threshold validation

3. **If approval is required**
 - Order is blocked
 - Status marked as *Requires Approval*

4. **Sales Order Approver**
 - Clicks **Approve Order**
 - Order becomes confirmable

---

## Technical Implementation

### Models Extended
- `res.partner`
- `credit_limit`
- `total_debt` (computed, stored)
- `sale.order`
- `requires_approval`
- `approved`
- `approval_threshold`

### Performance Considerations
- Outstanding debt is computed using:
- `read_group` (single SQL query)
- Avoids per-record invoice searches

### Security
- Custom group:
- `Sales Order Approver`
- Access restrictions enforced at:
- ORM level (`create`, `write`)
- Business logic level (`action_confirm`, `action_approve_order`)

---

## Module Structure

```bash
  odoo_sale_credit_approval/
  ├── models/
  │ ├── res_partner.py
  │ └── sale_order.py
  ├── views/
  │ ├── res_partner_view.xml
  │ └── sale_order_view.xml
  ├── security/
  │ └── security_groups.xml
  ├── manifest.py
  └── README.md
```

---

## Dependencies
- `sale`
- `account`

---

## Tested On
- Odoo 18 (Community Edition)

---

## Author
**Nguyen Quang Vinh**  
GitHub: https://github.com/vinhisreal

---

## Notes
This module was developed as a **learning and portfolio project** to demonstrate:
- Odoo ORM mastery
- Business logic design
- Security & approval workflows
- Clean module structure

