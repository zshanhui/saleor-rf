# Generated manually for B2B module

import uuid
from decimal import Decimal

import django.contrib.postgres.indexes
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import saleor.core.db.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("account", "0001_initial"),
        ("channel", "0001_initial"),
        ("order", "0001_initial"),
        ("product", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PartnershipTier",
            fields=[
                (
                    "private_metadata",
                    models.JSONField(
                        blank=True,
                        db_default={},
                        default=dict,
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        db_default={},
                        default=dict,
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("bronze", "Bronze"),
                            ("silver", "Silver"),
                            ("gold", "Gold"),
                            ("platinum", "Platinum"),
                            ("custom", "Custom"),
                        ],
                        default="custom",
                        max_length=32,
                    ),
                ),
                ("description", models.TextField(blank=True, default="")),
                (
                    "discount_percentage",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        help_text="Base discount percentage for this tier (e.g., 10.00 for 10%)",
                        max_digits=5,
                    ),
                ),
                (
                    "minimum_order_quantity",
                    models.PositiveIntegerField(
                        default=1, help_text="Minimum quantity per order"
                    ),
                ),
                (
                    "minimum_order_value_amount",
                    models.DecimalField(
                        decimal_places=3,
                        default=Decimal("0.00"),
                        help_text="Minimum order value in default currency",
                        max_digits=12,
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                (
                    "credit_limit_amount",
                    models.DecimalField(
                        decimal_places=3,
                        default=Decimal("0.00"),
                        help_text="Maximum credit limit for businesses in this tier",
                        max_digits=12,
                    ),
                ),
                (
                    "payment_terms_days",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Number of days for payment terms (0 = prepaid, 30 = NET 30, etc.)",
                    ),
                ),
                (
                    "priority",
                    models.PositiveIntegerField(
                        db_index=True,
                        default=0,
                        help_text="Priority for tier ordering (higher = better tier)",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("-priority", "name"),
            },
        ),
        migrations.CreateModel(
            name="Business",
            fields=[
                (
                    "private_metadata",
                    models.JSONField(
                        blank=True,
                        db_default={},
                        default=dict,
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        db_default={},
                        default=dict,
                    ),
                ),
                (
                    "external_reference",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=250,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                (
                    "tax_id",
                    models.CharField(
                        help_text="Business tax ID / VAT number / Registration number",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "company_registration_number",
                    models.CharField(blank=True, default="", max_length=100),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "verification_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending - Awaiting review"),
                            ("in_review", "In Review - Currently being reviewed"),
                            ("verified", "Verified - Business has been verified"),
                            ("rejected", "Rejected - Verification rejected"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                (
                    "credit_balance_amount",
                    models.DecimalField(
                        decimal_places=3,
                        default=Decimal("0.00"),
                        help_text="Current outstanding credit balance",
                        max_digits=12,
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("phone", models.CharField(blank=True, default="", max_length=50)),
                ("website", models.URLField(blank=True, default="")),
                ("note", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "billing_address",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="b2b_billing_businesses",
                        to="account.address",
                    ),
                ),
                (
                    "default_shipping_address",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="account.address",
                    ),
                ),
                (
                    "shipping_addresses",
                    models.ManyToManyField(
                        blank=True,
                        related_name="b2b_shipping_businesses",
                        to="account.address",
                    ),
                ),
                (
                    "tier",
                    models.ForeignKey(
                        help_text="Partnership tier determining pricing and credit terms",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="businesses",
                        to="b2b.partnershiptier",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="verified_businesses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Businesses",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="BusinessUser",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("owner", "Owner - Full access and ownership"),
                            ("admin", "Admin - Manage business settings and users"),
                            ("buyer", "Buyer - Can place orders"),
                            ("viewer", "Viewer - Read-only access"),
                        ],
                        default="buyer",
                        max_length=32,
                    ),
                ),
                ("can_place_orders", models.BooleanField(default=True)),
                ("can_view_orders", models.BooleanField(default=True)),
                ("can_manage_users", models.BooleanField(default=False)),
                ("can_manage_addresses", models.BooleanField(default=False)),
                ("can_view_credit", models.BooleanField(default=True)),
                (
                    "spending_limit_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        help_text="Maximum order value this user can place (null = unlimited)",
                        max_digits=12,
                        null=True,
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="b2b.business",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="business_memberships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("business", "-role", "user"),
                "unique_together": {("business", "user")},
            },
        ),
        migrations.CreateModel(
            name="TierPricing",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "price_amount",
                    models.DecimalField(decimal_places=3, max_digits=12),
                ),
                ("currency", models.CharField(max_length=3)),
                (
                    "minimum_quantity",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="Minimum quantity to qualify for this price",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tier_prices",
                        to="channel.channel",
                    ),
                ),
                (
                    "tier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tier_prices",
                        to="b2b.partnershiptier",
                    ),
                ),
                (
                    "variant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tier_prices",
                        to="product.productvariant",
                    ),
                ),
            ],
            options={
                "ordering": ("tier", "variant", "minimum_quantity"),
                "unique_together": {("tier", "variant", "channel", "minimum_quantity")},
            },
        ),
        migrations.CreateModel(
            name="BusinessOrder",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "purchase_order_number",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Customer's internal purchase order number",
                        max_length=100,
                    ),
                ),
                (
                    "is_credit_order",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this order uses credit terms",
                    ),
                ),
                (
                    "credit_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending - Awaiting payment"),
                            ("approved", "Approved - Credit approved"),
                            ("paid", "Paid - Payment received"),
                            ("overdue", "Overdue - Payment past due date"),
                            ("cancelled", "Cancelled - Order cancelled"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                (
                    "due_date",
                    models.DateField(
                        blank=True,
                        help_text="Payment due date for credit orders",
                        null=True,
                    ),
                ),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("tier_name", models.CharField(blank=True, default="", max_length=255)),
                (
                    "tier_discount_percentage",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=5
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orders",
                        to="b2b.business",
                    ),
                ),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="business_order",
                        to="order.order",
                    ),
                ),
                (
                    "placed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="b2b.businessuser",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="BusinessEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("type", models.CharField(max_length=255)),
                ("parameters", models.JSONField(blank=True, default=dict)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="b2b.business",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="b2b_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-date",),
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name="partnershiptier",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["private_metadata"], name="partnershiptier_p_meta_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="partnershiptier",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["metadata"], name="partnershiptier_meta_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="partnershiptier",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["slug"], name="partnershiptier_slug_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="partnershiptier",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["is_active"], name="partnershiptier_active_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="business",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["private_metadata"], name="business_p_meta_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="business",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["metadata"], name="business_meta_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="business",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["slug"], name="business_slug_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="business",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["tax_id"], name="business_tax_id_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="business",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["is_active"], name="business_active_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="business",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["verification_status"], name="business_verification_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="business",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["name", "tax_id"],
                name="business_search_gin",
                opclasses=["gin_trgm_ops", "gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="businessuser",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["role"], name="businessuser_role_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="businessuser",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["is_active"], name="businessuser_active_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tierpricing",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["variant", "channel"], name="tierpricing_variant_ch_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="tierpricing",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["tier", "minimum_quantity"], name="tierpricing_tier_qty_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="businessorder",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["business"], name="businessorder_business_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="businessorder",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["is_credit_order"], name="businessorder_credit_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="businessorder",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["credit_status"], name="businessorder_status_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="businessorder",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["due_date"], name="businessorder_due_date_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="businessorder",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["purchase_order_number"],
                name="businessorder_po_gin",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="businessevent",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["type"], name="businessevent_type_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="businessevent",
            index=django.contrib.postgres.indexes.BTreeIndex(
                fields=["date"], name="businessevent_date_idx"
            ),
        ),
    ]
