from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Optional

from prices import Money

if TYPE_CHECKING:
    from ..models import Business, PartnershipTier, TierPricing


def get_tier_price_for_variant(
    variant_id: int,
    channel_id: int,
    tier: "PartnershipTier",
    quantity: int = 1,
) -> Optional["TierPricing"]:
    """Get the best matching tier price for a variant based on quantity.

    Returns the tier pricing that matches the quantity threshold, prioritizing
    higher quantity thresholds for better prices.

    Args:
        variant_id: Product variant ID
        channel_id: Channel ID
        tier: Partnership tier
        quantity: Order quantity

    Returns:
        TierPricing instance or None if no tier pricing exists
    """
    from ..models import TierPricing

    # Get all tier prices for this variant/channel/tier combination
    # that the quantity qualifies for, ordered by minimum_quantity descending
    # to get the best price (higher quantity = better price)
    tier_pricing = (
        TierPricing.objects.filter(
            tier=tier,
            variant_id=variant_id,
            channel_id=channel_id,
            minimum_quantity__lte=quantity,
        )
        .order_by("-minimum_quantity")
        .first()
    )

    return tier_pricing


def apply_tier_discount(
    price: Money,
    tier: "PartnershipTier",
) -> Money:
    """Apply tier-based percentage discount to a price.

    Args:
        price: Original price
        tier: Partnership tier with discount percentage

    Returns:
        Discounted price
    """
    if tier.discount_percentage <= 0:
        return price

    discount_multiplier = (Decimal("100") - tier.discount_percentage) / Decimal("100")
    discounted_amount = (price.amount * discount_multiplier).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return Money(discounted_amount, price.currency)


def get_volume_discount(
    base_price: Money,
    quantity: int,
    tier: "PartnershipTier",
    variant_id: int,
    channel_id: int,
) -> Money:
    """Calculate the final price considering volume discounts.

    First checks for specific tier pricing, then applies tier percentage discount.

    Args:
        base_price: Base product price
        quantity: Order quantity
        tier: Partnership tier
        variant_id: Product variant ID
        channel_id: Channel ID

    Returns:
        Final discounted price
    """
    # First, check for specific tier pricing
    tier_pricing = get_tier_price_for_variant(
        variant_id=variant_id,
        channel_id=channel_id,
        tier=tier,
        quantity=quantity,
    )

    if tier_pricing:
        # Use the specific tier price
        return tier_pricing.price

    # Fall back to applying tier percentage discount
    return apply_tier_discount(base_price, tier)


def calculate_b2b_line_price(
    base_unit_price: Money,
    quantity: int,
    business: "Business",
    variant_id: int,
    channel_id: int,
) -> tuple[Money, Money]:
    """Calculate B2B line price with tier discounts.

    Args:
        base_unit_price: Base unit price before B2B discounts
        quantity: Line quantity
        business: Business placing the order
        variant_id: Product variant ID
        channel_id: Channel ID

    Returns:
        Tuple of (unit_price, total_price) after B2B discounts
    """
    if not business.is_verified or not business.is_active:
        # Non-verified businesses don't get B2B pricing
        return base_unit_price, Money(
            base_unit_price.amount * quantity, base_unit_price.currency
        )

    tier = business.tier
    unit_price = get_volume_discount(
        base_price=base_unit_price,
        quantity=quantity,
        tier=tier,
        variant_id=variant_id,
        channel_id=channel_id,
    )

    total_price = Money(unit_price.amount * quantity, unit_price.currency)

    return unit_price, total_price


def get_tier_discount_amount(
    original_price: Money,
    tier: "PartnershipTier",
) -> Money:
    """Calculate the discount amount for a tier.

    Args:
        original_price: Original price before discount
        tier: Partnership tier

    Returns:
        Discount amount as Money
    """
    discounted_price = apply_tier_discount(original_price, tier)
    discount_amount = original_price.amount - discounted_price.amount

    return Money(max(Decimal("0"), discount_amount), original_price.currency)
