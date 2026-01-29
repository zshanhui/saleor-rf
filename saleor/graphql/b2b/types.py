import graphene
from graphene import relay

from ...b2b import models
from ...permission.enums import B2BPermissions
from ..account.types import Address, User
from ..channel.types import Channel
from ..core import ResolveInfo
from ..core.connection import CountableConnection
from ..core.doc_category import DOC_CATEGORY_B2B
from ..core.fields import PermissionsField
from ..core.scalars import UUID
from ..core.types import ModelObjectType, Money, NonNullList
from ..meta.types import ObjectWithMetadata
from ..product.types import ProductVariant
from .enums import (
    BusinessUserRoleEnum,
    BusinessVerificationStatusEnum,
    CreditOrderStatusEnum,
    PartnershipTierTypeEnum,
)


class PartnershipTier(ModelObjectType[models.PartnershipTier]):
    """Represents a B2B partnership tier with associated benefits and pricing."""

    id = graphene.GlobalID(required=True, description="The ID of the partnership tier.")
    name = graphene.String(required=True, description="Name of the partnership tier.")
    slug = graphene.String(required=True, description="Slug of the partnership tier.")
    type = PartnershipTierTypeEnum(description="Type of the partnership tier.")
    description = graphene.String(description="Description of the tier benefits.")
    discount_percentage = graphene.Float(
        required=True, description="Base discount percentage for this tier."
    )
    minimum_order_quantity = graphene.Int(
        required=True, description="Minimum quantity per order."
    )
    minimum_order_value = graphene.Field(
        Money, description="Minimum order value required."
    )
    credit_limit = graphene.Field(
        Money, description="Maximum credit limit for businesses in this tier."
    )
    payment_terms_days = graphene.Int(
        required=True,
        description="Number of days for payment terms (0 = prepaid, 30 = NET 30).",
    )
    priority = graphene.Int(
        required=True, description="Priority for tier ordering (higher = better tier)."
    )
    is_active = graphene.Boolean(
        required=True, description="Whether the tier is active."
    )
    businesses_count = graphene.Int(
        description="Number of businesses in this tier.",
        permissions=[B2BPermissions.MANAGE_B2B],
    )

    class Meta:
        description = "Represents a B2B partnership tier."
        interfaces = [relay.Node, ObjectWithMetadata]
        model = models.PartnershipTier
        doc_category = DOC_CATEGORY_B2B

    @staticmethod
    def resolve_businesses_count(root: models.PartnershipTier, info: ResolveInfo):
        return root.businesses.count()

    @staticmethod
    def resolve_minimum_order_value(root: models.PartnershipTier, info: ResolveInfo):
        return root.minimum_order_value

    @staticmethod
    def resolve_credit_limit(root: models.PartnershipTier, info: ResolveInfo):
        return root.credit_limit


class PartnershipTierCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_B2B
        node = PartnershipTier


class Business(ModelObjectType[models.Business]):
    """Represents a B2B business/company entity."""

    id = graphene.GlobalID(required=True, description="The ID of the business.")
    name = graphene.String(required=True, description="Name of the business.")
    slug = graphene.String(required=True, description="Slug of the business.")
    tax_id = graphene.String(required=True, description="Business tax ID / VAT number.")
    company_registration_number = graphene.String(
        description="Company registration number."
    )
    tier = graphene.Field(
        PartnershipTier, required=True, description="Partnership tier of the business."
    )
    billing_address = graphene.Field(Address, description="Billing address.")
    shipping_addresses = NonNullList(
        Address, description="List of shipping addresses."
    )
    default_shipping_address = graphene.Field(
        Address, description="Default shipping address."
    )
    is_active = graphene.Boolean(
        required=True, description="Whether the business is active."
    )
    verification_status = BusinessVerificationStatusEnum(
        required=True, description="Verification status of the business."
    )
    is_verified = graphene.Boolean(
        required=True, description="Whether the business is verified."
    )
    credit_balance = graphene.Field(
        Money, description="Current outstanding credit balance."
    )
    available_credit = graphene.Field(
        Money, description="Available credit based on tier limit."
    )
    email = graphene.String(description="Contact email.")
    phone = graphene.String(description="Contact phone number.")
    website = graphene.String(description="Business website URL.")
    note = PermissionsField(
        graphene.String,
        description="Internal notes about the business.",
        permissions=[B2BPermissions.MANAGE_BUSINESSES],
    )
    members = NonNullList(
        lambda: BusinessUser,
        description="Members of the business.",
    )

    class Meta:
        description = "Represents a B2B business entity."
        interfaces = [relay.Node, ObjectWithMetadata]
        model = models.Business
        doc_category = DOC_CATEGORY_B2B

    @staticmethod
    def resolve_tier(root: models.Business, info: ResolveInfo):
        return root.tier

    @staticmethod
    def resolve_shipping_addresses(root: models.Business, info: ResolveInfo):
        return root.shipping_addresses.all()

    @staticmethod
    def resolve_credit_balance(root: models.Business, info: ResolveInfo):
        return root.credit_balance

    @staticmethod
    def resolve_available_credit(root: models.Business, info: ResolveInfo):
        from prices import Money as PricesMoney

        return PricesMoney(root.available_credit, root.currency)

    @staticmethod
    def resolve_members(root: models.Business, info: ResolveInfo):
        return root.members.all()


class BusinessCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_B2B
        node = Business


class BusinessUser(ModelObjectType[models.BusinessUser]):
    """Represents a user's membership in a business."""

    id = graphene.GlobalID(
        required=True, description="The ID of the business membership."
    )
    business = graphene.Field(
        Business, required=True, description="The business this user belongs to."
    )
    user = graphene.Field(User, required=True, description="The user.")
    role = BusinessUserRoleEnum(required=True, description="Role of the user.")
    can_place_orders = graphene.Boolean(
        required=True, description="Whether the user can place orders."
    )
    can_view_orders = graphene.Boolean(
        required=True, description="Whether the user can view orders."
    )
    can_manage_users = graphene.Boolean(
        required=True, description="Whether the user can manage other users."
    )
    can_manage_addresses = graphene.Boolean(
        required=True, description="Whether the user can manage addresses."
    )
    can_view_credit = graphene.Boolean(
        required=True, description="Whether the user can view credit information."
    )
    spending_limit = graphene.Field(
        Money, description="Maximum order value this user can place."
    )
    is_active = graphene.Boolean(
        required=True, description="Whether the membership is active."
    )
    is_owner = graphene.Boolean(
        required=True, description="Whether the user is the owner."
    )
    is_admin = graphene.Boolean(
        required=True, description="Whether the user is an admin."
    )

    class Meta:
        description = "Represents a user's membership in a business."
        interfaces = [relay.Node]
        model = models.BusinessUser
        doc_category = DOC_CATEGORY_B2B

    @staticmethod
    def resolve_spending_limit(root: models.BusinessUser, info: ResolveInfo):
        return root.spending_limit

    @staticmethod
    def resolve_is_owner(root: models.BusinessUser, info: ResolveInfo):
        return root.is_owner

    @staticmethod
    def resolve_is_admin(root: models.BusinessUser, info: ResolveInfo):
        return root.is_admin


class BusinessUserCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_B2B
        node = BusinessUser


class TierPricing(ModelObjectType[models.TierPricing]):
    """Represents tier-specific pricing for a product variant."""

    id = graphene.GlobalID(required=True, description="The ID of the tier pricing.")
    tier = graphene.Field(
        PartnershipTier, required=True, description="The partnership tier."
    )
    variant = graphene.Field(
        ProductVariant, required=True, description="The product variant."
    )
    channel = graphene.Field(Channel, required=True, description="The channel.")
    price = graphene.Field(Money, required=True, description="The tier price.")
    minimum_quantity = graphene.Int(
        required=True, description="Minimum quantity to qualify for this price."
    )

    class Meta:
        description = "Represents tier-specific pricing for a product variant."
        interfaces = [relay.Node]
        model = models.TierPricing
        doc_category = DOC_CATEGORY_B2B

    @staticmethod
    def resolve_price(root: models.TierPricing, info: ResolveInfo):
        return root.price


class TierPricingCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_B2B
        node = TierPricing


class BusinessOrder(ModelObjectType[models.BusinessOrder]):
    """Represents B2B-specific order information."""

    id = graphene.GlobalID(required=True, description="The ID of the business order.")
    order = graphene.Field(
        "saleor.graphql.order.types.Order",
        required=True,
        description="The associated order.",
    )
    business = graphene.Field(
        Business, required=True, description="The business that placed the order."
    )
    placed_by = graphene.Field(
        BusinessUser, description="The user who placed the order."
    )
    purchase_order_number = graphene.String(
        description="Customer's internal purchase order number."
    )
    is_credit_order = graphene.Boolean(
        required=True, description="Whether this order uses credit terms."
    )
    credit_status = CreditOrderStatusEnum(
        description="Status of credit payment for this order."
    )
    due_date = graphene.Date(description="Payment due date for credit orders.")
    is_overdue = graphene.Boolean(
        required=True, description="Whether the credit order is past due date."
    )
    tier_name = graphene.String(description="Tier name at the time of order.")
    tier_discount_percentage = graphene.Float(
        description="Tier discount percentage applied."
    )

    class Meta:
        description = "Represents B2B-specific order information."
        interfaces = [relay.Node]
        model = models.BusinessOrder
        doc_category = DOC_CATEGORY_B2B

    @staticmethod
    def resolve_is_overdue(root: models.BusinessOrder, info: ResolveInfo):
        return root.is_overdue


class BusinessOrderCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_B2B
        node = BusinessOrder
