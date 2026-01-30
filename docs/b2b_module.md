# B2B Wholesale Ordering Module

This document describes the B2B (Business-to-Business) wholesale ordering module for Saleor, which enables businesses to manage wholesale customers with tiered pricing, credit terms, and specialized ordering workflows.

## Table of Contents

- [Overview](#overview)
- [Partnership Tiers](#partnership-tiers)
- [Business Management](#business-management)
- [User Roles & Permissions](#user-roles--permissions)
- [Pricing Features](#pricing-features)
- [Credit Management](#credit-management)
- [GraphQL API Reference](#graphql-api-reference)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)

---

## Overview

The B2B module extends Saleor's capabilities to support wholesale operations with:

- **Partnership Tiers**: Define customer levels with different benefits
- **Business Accounts**: Manage company entities separate from individual users
- **Tiered Pricing**: Set custom prices based on partnership level and volume
- **Credit Terms**: Offer NET payment terms with credit limits
- **Order Management**: Track B2B orders with purchase order numbers

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      B2B Module                              │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐    ┌───────────────┐    ┌─────────────┐ │
│  │ Partnership   │───▶│   Business    │───▶│  Business   │ │
│  │    Tier       │    │               │    │    User     │ │
│  └───────────────┘    └───────────────┘    └─────────────┘ │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│  ┌───────────────┐    ┌───────────────┐    ┌─────────────┐ │
│  │ Tier Pricing  │    │Business Order │    │   Order     │ │
│  │  (per variant)│    │  (PO, credit) │    │  (Saleor)   │ │
│  └───────────────┘    └───────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Partnership Tiers

Partnership tiers define the benefits and requirements for B2B customers.

### Default Tier Structure

| Tier | Discount | Min Order Value | Min Quantity | Credit Limit | Payment Terms |
|------|----------|-----------------|--------------|--------------|---------------|
| Bronze | 5% | $500 | 10 | $0 | Prepaid |
| Silver | 10% | $1,000 | 25 | $5,000 | NET 15 |
| Gold | 15% | $2,500 | 50 | $15,000 | NET 30 |
| Platinum | 20% | $5,000 | 100 | $50,000 | NET 60 |

### Tier Properties

| Property | Description |
|----------|-------------|
| `name` | Display name of the tier |
| `slug` | URL-friendly identifier |
| `type` | Tier type (bronze/silver/gold/platinum/custom) |
| `discount_percentage` | Base percentage discount applied to all orders |
| `minimum_order_quantity` | Minimum items required per order |
| `minimum_order_value` | Minimum order value in currency |
| `credit_limit` | Maximum credit available for NET terms |
| `payment_terms_days` | Days for payment (0 = prepaid) |
| `priority` | Ordering priority (higher = better tier) |

---

## Business Management

### Business Entity

A Business represents a company or organization that can place wholesale orders.

**Key Fields:**
- `name`: Company name
- `slug`: Unique identifier
- `tax_id`: Business tax ID / VAT number (unique)
- `tier`: Associated partnership tier
- `verification_status`: Pending → In Review → Verified/Rejected
- `credit_balance`: Current outstanding credit amount
- `billing_address`: Primary billing address
- `shipping_addresses`: Multiple shipping locations

### Verification Workflow

```
┌─────────┐     ┌───────────┐     ┌──────────┐
│ Pending │────▶│ In Review │────▶│ Verified │
└─────────┘     └───────────┘     └──────────┘
                      │                  
                      ▼                  
                ┌──────────┐            
                │ Rejected │            
                └──────────┘            
```

Only **verified** businesses can:
- Receive tier discounts
- Use credit terms
- Access B2B-specific features

---

## User Roles & Permissions

### Business User Roles

| Role | Description | Default Permissions |
|------|-------------|---------------------|
| **Owner** | Full access and ownership | All permissions |
| **Admin** | Manage business settings and users | All except ownership transfer |
| **Buyer** | Can place orders | Place orders, view orders, view credit |
| **Viewer** | Read-only access | View orders only |

### Permission Matrix

| Permission | Owner | Admin | Buyer | Viewer |
|------------|-------|-------|-------|--------|
| `can_place_orders` | ✓ | ✓ | ✓ | ✗ |
| `can_view_orders` | ✓ | ✓ | ✓ | ✓ |
| `can_manage_users` | ✓ | ✓ | ✗ | ✗ |
| `can_manage_addresses` | ✓ | ✓ | ✗ | ✗ |
| `can_view_credit` | ✓ | ✓ | ✓ | ✗ |

### Spending Limits

Individual users can have spending limits that cap the maximum order value they can place, providing additional control for business administrators.

---

## Pricing Features

### Tier-Based Discounts

All products automatically receive the tier's base discount percentage:

```
Final Price = Base Price × (1 - Tier Discount %)

Example (Silver tier, 10% discount):
Base Price: $100.00
Final Price: $100.00 × 0.90 = $90.00
```

### Volume-Based Pricing

Custom prices can be set per tier/variant/channel combination with quantity thresholds:

| Tier | Variant | Min Qty | Price |
|------|---------|---------|-------|
| Silver | SKU-001 | 1 | $95.00 |
| Silver | SKU-001 | 10 | $90.00 |
| Silver | SKU-001 | 50 | $85.00 |
| Gold | SKU-001 | 1 | $90.00 |
| Gold | SKU-001 | 25 | $82.00 |

The system selects the best applicable price based on the order quantity.

### Pricing Priority

1. **Tier-Specific Volume Price** (if exists for quantity threshold)
2. **Tier Percentage Discount** (applied to base price)
3. **Base Price** (for non-verified businesses)

---

## Credit Management

### Credit Terms

Businesses with `payment_terms_days > 0` can use credit:

| Payment Terms | Description |
|---------------|-------------|
| NET 0 (Prepaid) | Payment required before order |
| NET 15 | Payment due in 15 days |
| NET 30 | Payment due in 30 days |
| NET 60 | Payment due in 60 days |

### Credit Workflow

```python
# Check available credit
available = credit_limit - credit_balance

# On order placement (credit order)
credit_balance += order_total
due_date = order_date + payment_terms_days

# On payment received
credit_balance -= payment_amount
credit_status = "paid"
```

### Credit Order Status

| Status | Description |
|--------|-------------|
| `pending` | Awaiting payment |
| `approved` | Credit approved, order processing |
| `paid` | Payment received |
| `overdue` | Past due date |
| `cancelled` | Order cancelled |

---

## GraphQL API Reference

### Queries

#### Get Partnership Tiers

```graphql
query {
  partnershipTiers(first: 10) {
    edges {
      node {
        id
        name
        slug
        discountPercentage
        creditLimit {
          amount
          currency
        }
        paymentTermsDays
        businessesCount
      }
    }
  }
}
```

#### Get Single Tier

```graphql
query {
  partnershipTier(slug: "gold") {
    id
    name
    discountPercentage
    minimumOrderValue {
      amount
      currency
    }
  }
}
```

#### Get Businesses

```graphql
query {
  businesses(first: 10) {
    edges {
      node {
        id
        name
        taxId
        tier {
          name
        }
        verificationStatus
        creditBalance {
          amount
          currency
        }
        availableCredit {
          amount
          currency
        }
        members {
          user {
            email
          }
          role
        }
      }
    }
  }
}
```

#### Get Current User's Business

```graphql
query {
  businessByUser {
    id
    name
    tier {
      name
      discountPercentage
    }
    isVerified
  }
}
```

### Mutations

#### Create Partnership Tier

```graphql
mutation {
  partnershipTierCreate(input: {
    name: "Enterprise"
    slug: "enterprise"
    type: CUSTOM
    discountPercentage: 25.0
    minimumOrderValue: 10000.00
    minimumOrderQuantity: 200
    creditLimit: 100000.00
    paymentTermsDays: 90
    currency: "USD"
    priority: 50
  }) {
    partnershipTier {
      id
      name
    }
    b2bErrors {
      field
      message
      code
    }
  }
}
```

#### Create Business

```graphql
mutation {
  businessCreate(input: {
    name: "Acme Corporation"
    taxId: "US-123456789"
    tierId: "UGFydG5lcnNoaXBUaWVyOjEyMw=="
    email: "orders@acme.com"
    phone: "+1-555-0100"
    billingAddress: {
      firstName: "John"
      lastName: "Doe"
      companyName: "Acme Corporation"
      streetAddress1: "123 Business Ave"
      city: "New York"
      postalCode: "10001"
      country: US
    }
  }) {
    business {
      id
      name
      verificationStatus
    }
    b2bErrors {
      field
      message
    }
  }
}
```

#### Verify Business

```graphql
mutation {
  businessVerify(
    id: "QnVzaW5lc3M6MTIz"
    input: { status: VERIFIED }
  ) {
    business {
      id
      verificationStatus
      verifiedAt
    }
  }
}
```

#### Add User to Business

```graphql
mutation {
  businessUserCreate(input: {
    businessId: "QnVzaW5lc3M6MTIz"
    userId: "VXNlcjo0NTY="
    role: BUYER
    spendingLimit: 5000.00
    currency: "USD"
  }) {
    businessUser {
      id
      role
      spendingLimit {
        amount
        currency
      }
    }
  }
}
```

#### Create Tier Pricing

```graphql
mutation {
  tierPricingBulkCreate(input: [
    {
      tierId: "UGFydG5lcnNoaXBUaWVyOjE="
      variantId: "UHJvZHVjdFZhcmlhbnQ6MTIz"
      channelId: "Q2hhbm5lbDox"
      price: 85.00
      currency: "USD"
      minimumQuantity: 10
    },
    {
      tierId: "UGFydG5lcnNoaXBUaWVyOjE="
      variantId: "UHJvZHVjdFZhcmlhbnQ6MTIz"
      channelId: "Q2hhbm5lbDox"
      price: 75.00
      currency: "USD"
      minimumQuantity: 50
    }
  ]) {
    tierPricings {
      id
      price {
        amount
        currency
      }
      minimumQuantity
    }
    count
  }
}
```

---

## Usage Examples

### Setting Up B2B for a New Customer

```python
# 1. Create or select a partnership tier
tier = PartnershipTier.objects.get(slug="silver")

# 2. Create the business
business = Business.objects.create(
    name="New Wholesale Client",
    slug="new-wholesale-client",
    tax_id="TAX-123456",
    tier=tier,
    email="orders@newclient.com",
)

# 3. Add the primary contact as owner
BusinessUser.objects.create(
    business=business,
    user=user,
    role=BusinessUserRole.OWNER,
)

# 4. Verify the business (admin action)
business.verification_status = BusinessVerificationStatus.VERIFIED
business.verified_at = timezone.now()
business.verified_by = admin_user
business.save()
```

### Calculating B2B Price

```python
from saleor.b2b.utils.pricing import calculate_b2b_line_price

# Get the B2B price for a line item
unit_price, total_price = calculate_b2b_line_price(
    base_unit_price=Money(100, "USD"),
    quantity=25,
    business=business,
    variant_id=variant.id,
    channel_id=channel.id,
)
```

### Processing Credit Orders

```python
from saleor.b2b.utils.credit import (
    check_credit_limit,
    process_credit_order,
    mark_credit_order_paid,
)

# Check if credit is available
can_use, message = check_credit_limit(business, order_total)

if can_use:
    # Process the credit order
    business_order.is_credit_order = True
    success = process_credit_order(business_order)
    
# When payment is received
mark_credit_order_paid(business_order)
```

---

## Configuration

### Required Permissions

Add the following permissions to staff users who manage B2B:

| Permission | Scope |
|------------|-------|
| `MANAGE_B2B` | Full B2B module access |
| `MANAGE_BUSINESSES` | Create/edit/verify businesses |
| `MANAGE_PARTNERSHIP_TIERS` | Manage tiers and pricing |
| `MANAGE_B2B_ORDERS` | View and manage B2B orders |

### Environment Variables

No additional environment variables are required. The B2B module uses existing Saleor configuration.

### Database Migration

After enabling the B2B module, run migrations:

```bash
python manage.py migrate b2b
```

### Setting Up Default Tiers

You can create default tiers programmatically:

```python
from decimal import Decimal
from saleor.b2b.models import PartnershipTier
from saleor.b2b import PartnershipTierType

tiers = [
    {
        "name": "Bronze",
        "slug": "bronze",
        "type": PartnershipTierType.BRONZE,
        "discount_percentage": Decimal("5.00"),
        "minimum_order_value_amount": Decimal("500.00"),
        "credit_limit_amount": Decimal("0.00"),
        "payment_terms_days": 0,
        "priority": 10,
    },
    {
        "name": "Silver",
        "slug": "silver",
        "type": PartnershipTierType.SILVER,
        "discount_percentage": Decimal("10.00"),
        "minimum_order_value_amount": Decimal("1000.00"),
        "credit_limit_amount": Decimal("5000.00"),
        "payment_terms_days": 15,
        "priority": 20,
    },
    # ... Gold, Platinum
]

for tier_data in tiers:
    PartnershipTier.objects.get_or_create(
        slug=tier_data["slug"],
        defaults=tier_data,
    )
```

---

## Future Enhancements

The following features are planned for future releases:

- [ ] Bulk order import (CSV/Excel)
- [ ] Order approval workflows
- [ ] Recurring orders / subscriptions
- [ ] Credit payment reminders
- [ ] Business-specific catalogs
- [ ] Quantity break pricing rules
- [ ] Integration with accounting systems

---

## Support

For issues or questions regarding the B2B module, please:

1. Check the [Saleor documentation](https://docs.saleor.io)
2. Search existing [GitHub issues](https://github.com/saleor/saleor/issues)
3. Open a new issue with the `b2b` label
