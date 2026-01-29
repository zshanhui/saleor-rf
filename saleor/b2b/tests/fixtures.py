import pytest
from decimal import Decimal

from ...b2b import BusinessUserRole, BusinessVerificationStatus, PartnershipTierType
from ...b2b.models import (
    Business,
    BusinessUser,
    PartnershipTier,
    TierPricing,
)


@pytest.fixture
def partnership_tier_bronze(db):
    """Create a Bronze partnership tier."""
    return PartnershipTier.objects.create(
        name="Bronze",
        slug="bronze",
        type=PartnershipTierType.BRONZE,
        description="Entry level partnership",
        discount_percentage=Decimal("5.00"),
        minimum_order_quantity=10,
        minimum_order_value_amount=Decimal("500.00"),
        currency="USD",
        credit_limit_amount=Decimal("0.00"),
        payment_terms_days=0,
        priority=10,
        is_active=True,
    )


@pytest.fixture
def partnership_tier_silver(db):
    """Create a Silver partnership tier."""
    return PartnershipTier.objects.create(
        name="Silver",
        slug="silver",
        type=PartnershipTierType.SILVER,
        description="Mid level partnership",
        discount_percentage=Decimal("10.00"),
        minimum_order_quantity=25,
        minimum_order_value_amount=Decimal("1000.00"),
        currency="USD",
        credit_limit_amount=Decimal("5000.00"),
        payment_terms_days=15,
        priority=20,
        is_active=True,
    )


@pytest.fixture
def partnership_tier_gold(db):
    """Create a Gold partnership tier."""
    return PartnershipTier.objects.create(
        name="Gold",
        slug="gold",
        type=PartnershipTierType.GOLD,
        description="Premium partnership",
        discount_percentage=Decimal("15.00"),
        minimum_order_quantity=50,
        minimum_order_value_amount=Decimal("2500.00"),
        currency="USD",
        credit_limit_amount=Decimal("15000.00"),
        payment_terms_days=30,
        priority=30,
        is_active=True,
    )


@pytest.fixture
def partnership_tier_platinum(db):
    """Create a Platinum partnership tier."""
    return PartnershipTier.objects.create(
        name="Platinum",
        slug="platinum",
        type=PartnershipTierType.PLATINUM,
        description="Top level partnership",
        discount_percentage=Decimal("20.00"),
        minimum_order_quantity=100,
        minimum_order_value_amount=Decimal("5000.00"),
        currency="USD",
        credit_limit_amount=Decimal("50000.00"),
        payment_terms_days=60,
        priority=40,
        is_active=True,
    )


@pytest.fixture
def business(db, partnership_tier_silver):
    """Create a test business."""
    return Business.objects.create(
        name="Test Company Inc.",
        slug="test-company-inc",
        tax_id="US123456789",
        tier=partnership_tier_silver,
        verification_status=BusinessVerificationStatus.VERIFIED,
        is_active=True,
        email="contact@testcompany.com",
        phone="+1-555-123-4567",
    )


@pytest.fixture
def business_unverified(db, partnership_tier_bronze):
    """Create an unverified test business."""
    return Business.objects.create(
        name="New Company LLC",
        slug="new-company-llc",
        tax_id="US987654321",
        tier=partnership_tier_bronze,
        verification_status=BusinessVerificationStatus.PENDING,
        is_active=True,
        email="contact@newcompany.com",
    )


@pytest.fixture
def business_user_owner(db, business, customer_user):
    """Create a business user with owner role."""
    return BusinessUser.objects.create(
        business=business,
        user=customer_user,
        role=BusinessUserRole.OWNER,
        is_active=True,
    )


@pytest.fixture
def business_user_buyer(db, business, staff_user):
    """Create a business user with buyer role."""
    return BusinessUser.objects.create(
        business=business,
        user=staff_user,
        role=BusinessUserRole.BUYER,
        spending_limit_amount=Decimal("5000.00"),
        currency="USD",
        is_active=True,
    )
