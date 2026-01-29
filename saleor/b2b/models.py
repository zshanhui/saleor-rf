from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.indexes import BTreeIndex, GinIndex
from django.db import models
from django.utils import timezone

from ..core.db.fields import MoneyField
from ..core.models import ModelWithExternalReference, ModelWithMetadata
from . import BusinessUserRole, BusinessVerificationStatus, PartnershipTierType
from .enums import CreditOrderStatus


class PartnershipTier(ModelWithMetadata):
    """Defines different B2B partnership levels with associated benefits.

    Partnership tiers determine pricing discounts, credit limits, payment terms,
    and minimum order requirements for B2B customers.
    """

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid4)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    type = models.CharField(
        max_length=32,
        choices=PartnershipTierType.CHOICES,
        default=PartnershipTierType.CUSTOM,
    )
    description = models.TextField(blank=True, default="")

    # Discount configuration
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Base discount percentage for this tier (e.g., 10.00 for 10%)",
    )

    # Order requirements
    minimum_order_quantity = models.PositiveIntegerField(
        default=1, help_text="Minimum quantity per order"
    )
    minimum_order_value_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Minimum order value in default currency",
    )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default="USD",
    )
    minimum_order_value = MoneyField(
        amount_field="minimum_order_value_amount", currency_field="currency"
    )

    # Credit configuration
    credit_limit_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Maximum credit limit for businesses in this tier",
    )
    credit_limit = MoneyField(
        amount_field="credit_limit_amount", currency_field="currency"
    )
    payment_terms_days = models.PositiveIntegerField(
        default=0,
        help_text="Number of days for payment terms (0 = prepaid, 30 = NET 30, etc.)",
    )

    # Tier ordering
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Priority for tier ordering (higher = better tier)",
        db_index=True,
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-priority", "name")
        indexes = [
            *ModelWithMetadata.Meta.indexes,
            BTreeIndex(fields=["slug"], name="partnershiptier_slug_idx"),
            BTreeIndex(fields=["is_active"], name="partnershiptier_active_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}% discount)"

    def __repr__(self):
        return f"<PartnershipTier: {self.name} (priority={self.priority})>"


class Business(ModelWithMetadata, ModelWithExternalReference):
    """B2B Business/Company entity.

    Represents a registered business that can place wholesale orders.
    Each business is associated with a partnership tier and can have
    multiple users with different roles.
    """

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid4)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    # Business identification
    tax_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Business tax ID / VAT number / Registration number",
    )
    company_registration_number = models.CharField(
        max_length=100, blank=True, default=""
    )

    # Partnership
    tier = models.ForeignKey(
        PartnershipTier,
        related_name="businesses",
        on_delete=models.PROTECT,
        help_text="Partnership tier determining pricing and credit terms",
    )

    # Addresses
    billing_address = models.ForeignKey(
        "account.Address",
        related_name="b2b_billing_businesses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    shipping_addresses = models.ManyToManyField(
        "account.Address",
        related_name="b2b_shipping_businesses",
        blank=True,
    )
    default_shipping_address = models.ForeignKey(
        "account.Address",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Status
    is_active = models.BooleanField(default=True)
    verification_status = models.CharField(
        max_length=32,
        choices=BusinessVerificationStatus.CHOICES,
        default=BusinessVerificationStatus.PENDING,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        "account.User",
        related_name="verified_businesses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Credit tracking
    credit_balance_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.00"),
        help_text="Current outstanding credit balance",
    )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default="USD",
    )
    credit_balance = MoneyField(
        amount_field="credit_balance_amount", currency_field="currency"
    )

    # Contact information
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    website = models.URLField(blank=True, default="")

    # Notes
    note = models.TextField(blank=True, default="")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Businesses"
        indexes = [
            *ModelWithMetadata.Meta.indexes,
            BTreeIndex(fields=["slug"], name="business_slug_idx"),
            BTreeIndex(fields=["tax_id"], name="business_tax_id_idx"),
            BTreeIndex(fields=["is_active"], name="business_active_idx"),
            BTreeIndex(
                fields=["verification_status"], name="business_verification_idx"
            ),
            GinIndex(
                name="business_search_gin",
                fields=["name", "tax_id"],
                opclasses=["gin_trgm_ops"] * 2,
            ),
        ]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Business: {self.name} (tier={self.tier.name})>"

    @property
    def is_verified(self):
        return self.verification_status == BusinessVerificationStatus.VERIFIED

    @property
    def available_credit(self):
        """Calculate available credit based on tier limit and current balance."""
        if not self.tier:
            return Decimal("0.00")
        return max(
            Decimal("0.00"),
            self.tier.credit_limit_amount - self.credit_balance_amount,
        )

    def can_use_credit(self, amount: Decimal) -> bool:
        """Check if business can use the specified credit amount."""
        return (
            self.is_active
            and self.is_verified
            and self.tier.payment_terms_days > 0
            and amount <= self.available_credit
        )


class BusinessUser(models.Model):
    """Links Users to Businesses with specific roles and permissions.

    A user can belong to multiple businesses, and each business can have
    multiple users with different roles.
    """

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid4)
    business = models.ForeignKey(
        Business,
        related_name="members",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "account.User",
        related_name="business_memberships",
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        max_length=32,
        choices=BusinessUserRole.CHOICES,
        default=BusinessUserRole.BUYER,
    )

    # Permissions
    can_place_orders = models.BooleanField(default=True)
    can_view_orders = models.BooleanField(default=True)
    can_manage_users = models.BooleanField(default=False)
    can_manage_addresses = models.BooleanField(default=False)
    can_view_credit = models.BooleanField(default=True)

    # Spending limits
    spending_limit_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        null=True,
        blank=True,
        help_text="Maximum order value this user can place (null = unlimited)",
    )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default="USD",
    )
    spending_limit = MoneyField(
        amount_field="spending_limit_amount", currency_field="currency"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["business", "user"]]
        ordering = ("business", "-role", "user")
        indexes = [
            BTreeIndex(fields=["role"], name="businessuser_role_idx"),
            BTreeIndex(fields=["is_active"], name="businessuser_active_idx"),
        ]

    def __str__(self):
        return f"{self.user.email} @ {self.business.name} ({self.role})"

    def __repr__(self):
        return f"<BusinessUser: {self.user.email} @ {self.business.name}>"

    @property
    def is_owner(self):
        return self.role == BusinessUserRole.OWNER

    @property
    def is_admin(self):
        return self.role in [BusinessUserRole.OWNER, BusinessUserRole.ADMIN]

    def can_spend(self, amount: Decimal) -> bool:
        """Check if user can spend the specified amount."""
        if not self.can_place_orders or not self.is_active:
            return False
        if self.spending_limit_amount is None:
            return True
        return amount <= self.spending_limit_amount

    def save(self, *args, **kwargs):
        # Auto-set permissions based on role
        if self.role == BusinessUserRole.OWNER:
            self.can_place_orders = True
            self.can_view_orders = True
            self.can_manage_users = True
            self.can_manage_addresses = True
            self.can_view_credit = True
        elif self.role == BusinessUserRole.ADMIN:
            self.can_place_orders = True
            self.can_view_orders = True
            self.can_manage_users = True
            self.can_manage_addresses = True
            self.can_view_credit = True
        elif self.role == BusinessUserRole.VIEWER:
            self.can_place_orders = False
            self.can_manage_users = False
            self.can_manage_addresses = False
        super().save(*args, **kwargs)


class TierPricing(models.Model):
    """Tier-specific pricing for product variants.

    Allows setting custom prices for specific variants based on partnership tier.
    Supports volume-based pricing with quantity thresholds.
    """

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid4)
    tier = models.ForeignKey(
        PartnershipTier,
        related_name="tier_prices",
        on_delete=models.CASCADE,
    )
    variant = models.ForeignKey(
        "product.ProductVariant",
        related_name="tier_prices",
        on_delete=models.CASCADE,
    )
    channel = models.ForeignKey(
        "channel.Channel",
        related_name="tier_prices",
        on_delete=models.CASCADE,
    )

    # Price
    price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
    )
    price = MoneyField(amount_field="price_amount", currency_field="currency")

    # Volume discount threshold
    minimum_quantity = models.PositiveIntegerField(
        default=1,
        help_text="Minimum quantity to qualify for this price",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["tier", "variant", "channel", "minimum_quantity"]]
        ordering = ("tier", "variant", "minimum_quantity")
        indexes = [
            BTreeIndex(fields=["variant", "channel"], name="tierpricing_variant_ch_idx"),
            BTreeIndex(
                fields=["tier", "minimum_quantity"], name="tierpricing_tier_qty_idx"
            ),
        ]

    def __str__(self):
        return f"{self.variant} @ {self.tier.name}: {self.price} (min qty: {self.minimum_quantity})"


class BusinessOrder(models.Model):
    """Links Orders to Business context.

    Extends order information with B2B-specific data like purchase order numbers,
    credit terms, and business user who placed the order.
    """

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid4)
    order = models.OneToOneField(
        "order.Order",
        related_name="business_order",
        on_delete=models.CASCADE,
    )
    business = models.ForeignKey(
        Business,
        related_name="orders",
        on_delete=models.PROTECT,
    )
    placed_by = models.ForeignKey(
        BusinessUser,
        related_name="orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Purchase order
    purchase_order_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Customer's internal purchase order number",
    )

    # Credit order information
    is_credit_order = models.BooleanField(
        default=False,
        help_text="Whether this order uses credit terms",
    )
    credit_status = models.CharField(
        max_length=32,
        choices=CreditOrderStatus.CHOICES,
        default=CreditOrderStatus.PENDING,
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Payment due date for credit orders",
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    # Applied tier information (snapshot at order time)
    tier_name = models.CharField(max_length=255, blank=True, default="")
    tier_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            BTreeIndex(fields=["business"], name="businessorder_business_idx"),
            BTreeIndex(fields=["is_credit_order"], name="businessorder_credit_idx"),
            BTreeIndex(fields=["credit_status"], name="businessorder_status_idx"),
            BTreeIndex(fields=["due_date"], name="businessorder_due_date_idx"),
            GinIndex(
                name="businessorder_po_gin",
                fields=["purchase_order_number"],
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def __str__(self):
        po = f" (PO: {self.purchase_order_number})" if self.purchase_order_number else ""
        return f"Order {self.order.number} - {self.business.name}{po}"

    @property
    def is_overdue(self):
        """Check if credit order is past due date."""
        if not self.is_credit_order or not self.due_date:
            return False
        if self.credit_status == CreditOrderStatus.PAID:
            return False
        return timezone.now().date() > self.due_date

    def calculate_due_date(self):
        """Calculate due date based on business tier payment terms."""
        if self.business.tier.payment_terms_days > 0:
            from datetime import timedelta

            return timezone.now().date() + timedelta(
                days=self.business.tier.payment_terms_days
            )
        return None


class BusinessEvent(models.Model):
    """Tracks events related to B2B businesses."""

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid4)
    date = models.DateTimeField(default=timezone.now, editable=False)
    type = models.CharField(max_length=255)
    business = models.ForeignKey(
        Business,
        related_name="events",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "account.User",
        related_name="b2b_events",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    parameters = models.JSONField(blank=True, default=dict)

    class Meta:
        ordering = ("-date",)
        indexes = [
            BTreeIndex(fields=["type"], name="businessevent_type_idx"),
            BTreeIndex(fields=["date"], name="businessevent_date_idx"),
        ]

    def __str__(self):
        return f"{self.type} - {self.business.name} ({self.date})"
