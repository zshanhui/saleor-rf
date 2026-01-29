from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction
from prices import Money

if TYPE_CHECKING:
    from ..models import Business, BusinessOrder


def get_credit_balance(business: "Business") -> Money:
    """Get the current credit balance for a business.

    Args:
        business: Business instance

    Returns:
        Current credit balance as Money
    """
    return Money(business.credit_balance_amount, business.currency)


def calculate_available_credit(business: "Business") -> Money:
    """Calculate available credit for a business.

    Available credit = Tier credit limit - Current credit balance

    Args:
        business: Business instance

    Returns:
        Available credit as Money
    """
    if not business.tier or business.tier.payment_terms_days == 0:
        return Money(Decimal("0.00"), business.currency)

    available = business.tier.credit_limit_amount - business.credit_balance_amount
    return Money(max(Decimal("0.00"), available), business.currency)


def check_credit_limit(business: "Business", amount: Decimal) -> tuple[bool, str]:
    """Check if a business can use the specified credit amount.

    Args:
        business: Business instance
        amount: Amount to check

    Returns:
        Tuple of (can_use, message)
    """
    if not business.is_active:
        return False, "Business account is not active"

    if not business.is_verified:
        return False, "Business account is not verified"

    if not business.tier:
        return False, "Business has no partnership tier assigned"

    if business.tier.payment_terms_days == 0:
        return False, "Partnership tier does not support credit terms"

    available = calculate_available_credit(business)
    if amount > available.amount:
        return (
            False,
            f"Credit limit exceeded. Available: {available}, Requested: {amount}",
        )

    return True, "Credit available"


@transaction.atomic
def update_credit_balance(
    business: "Business",
    amount: Decimal,
    increase: bool = True,
) -> Money:
    """Update the credit balance for a business.

    Args:
        business: Business instance
        amount: Amount to add or subtract
        increase: If True, increase balance; if False, decrease

    Returns:
        New credit balance as Money
    """
    # Lock the business row for update
    business = (
        business.__class__.objects.select_for_update().get(pk=business.pk)
    )

    if increase:
        business.credit_balance_amount += amount
    else:
        business.credit_balance_amount = max(
            Decimal("0.00"), business.credit_balance_amount - amount
        )

    business.save(update_fields=["credit_balance_amount", "updated_at"])

    return Money(business.credit_balance_amount, business.currency)


def process_credit_order(business_order: "BusinessOrder") -> bool:
    """Process a credit order by updating the business credit balance.

    Args:
        business_order: BusinessOrder instance

    Returns:
        True if successful, False otherwise
    """
    if not business_order.is_credit_order:
        return True

    order = business_order.order
    business = business_order.business

    # Check credit limit
    can_use, message = check_credit_limit(business, order.total_gross_amount)
    if not can_use:
        return False

    # Update credit balance
    update_credit_balance(business, order.total_gross_amount, increase=True)

    # Set due date
    business_order.due_date = business_order.calculate_due_date()
    business_order.save(update_fields=["due_date", "updated_at"])

    return True


@transaction.atomic
def mark_credit_order_paid(business_order: "BusinessOrder") -> bool:
    """Mark a credit order as paid and update credit balance.

    Args:
        business_order: BusinessOrder instance

    Returns:
        True if successful
    """
    from django.utils import timezone

    from ..enums import CreditOrderStatus

    if not business_order.is_credit_order:
        return True

    # Reduce credit balance
    order = business_order.order
    update_credit_balance(
        business_order.business, order.total_gross_amount, increase=False
    )

    # Update order status
    business_order.credit_status = CreditOrderStatus.PAID
    business_order.paid_at = timezone.now()
    business_order.save(update_fields=["credit_status", "paid_at", "updated_at"])

    return True


def get_overdue_credit_orders(business: "Business" = None):
    """Get all overdue credit orders, optionally filtered by business.

    Args:
        business: Optional business to filter by

    Returns:
        QuerySet of overdue BusinessOrder instances
    """
    from django.utils import timezone

    from ..enums import CreditOrderStatus
    from ..models import BusinessOrder

    queryset = BusinessOrder.objects.filter(
        is_credit_order=True,
        due_date__lt=timezone.now().date(),
    ).exclude(credit_status=CreditOrderStatus.PAID)

    if business:
        queryset = queryset.filter(business=business)

    return queryset.select_related("order", "business")
