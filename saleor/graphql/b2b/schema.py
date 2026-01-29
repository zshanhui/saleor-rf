import graphene

from ...permission.enums import B2BPermissions
from ..core import ResolveInfo
from ..core.connection import create_connection_slice, filter_connection_queryset
from ..core.doc_category import DOC_CATEGORY_B2B
from ..core.fields import BaseField, FilterConnectionField, PermissionsField
from ..core.types import NonNullList
from .mutations import (
    BusinessCreate,
    BusinessDelete,
    BusinessUpdate,
    BusinessUserCreate,
    BusinessUserDelete,
    BusinessUserUpdate,
    BusinessVerify,
    PartnershipTierCreate,
    PartnershipTierDelete,
    PartnershipTierUpdate,
    TierPricingBulkCreate,
    TierPricingDelete,
)
from .resolvers import (
    resolve_business,
    resolve_business_by_user,
    resolve_business_orders,
    resolve_businesses,
    resolve_partnership_tier,
    resolve_partnership_tiers,
    resolve_tier_pricings,
)
from .types import (
    Business,
    BusinessCountableConnection,
    BusinessOrder,
    BusinessOrderCountableConnection,
    PartnershipTier,
    PartnershipTierCountableConnection,
    TierPricing,
    TierPricingCountableConnection,
)


class B2BQueries(graphene.ObjectType):
    partnership_tier = BaseField(
        PartnershipTier,
        id=graphene.Argument(graphene.ID, description="ID of the partnership tier."),
        slug=graphene.Argument(graphene.String, description="Slug of the tier."),
        description="Look up a partnership tier by ID or slug.",
        doc_category=DOC_CATEGORY_B2B,
    )
    partnership_tiers = PermissionsField(
        PartnershipTierCountableConnection,
        description="List all partnership tiers.",
        permissions=[B2BPermissions.MANAGE_B2B],
        doc_category=DOC_CATEGORY_B2B,
    )

    business = PermissionsField(
        Business,
        id=graphene.Argument(graphene.ID, description="ID of the business."),
        slug=graphene.Argument(graphene.String, description="Slug of the business."),
        description="Look up a business by ID or slug.",
        permissions=[B2BPermissions.MANAGE_BUSINESSES],
        doc_category=DOC_CATEGORY_B2B,
    )
    businesses = PermissionsField(
        BusinessCountableConnection,
        description="List all businesses.",
        permissions=[B2BPermissions.MANAGE_BUSINESSES],
        doc_category=DOC_CATEGORY_B2B,
    )
    business_by_user = BaseField(
        Business,
        description="Get the business associated with the current authenticated user.",
        doc_category=DOC_CATEGORY_B2B,
    )

    tier_pricings = PermissionsField(
        TierPricingCountableConnection,
        tier_id=graphene.Argument(graphene.ID, description="Filter by tier ID."),
        variant_id=graphene.Argument(graphene.ID, description="Filter by variant ID."),
        description="List tier-specific pricings.",
        permissions=[B2BPermissions.MANAGE_PARTNERSHIP_TIERS],
        doc_category=DOC_CATEGORY_B2B,
    )

    business_orders = PermissionsField(
        BusinessOrderCountableConnection,
        business_id=graphene.Argument(graphene.ID, description="Filter by business ID."),
        description="List B2B business orders.",
        permissions=[B2BPermissions.MANAGE_B2B_ORDERS],
        doc_category=DOC_CATEGORY_B2B,
    )

    @staticmethod
    def resolve_partnership_tier(_root, info: ResolveInfo, *, id=None, slug=None):
        return resolve_partnership_tier(info, id=id, slug=slug)

    @staticmethod
    def resolve_partnership_tiers(_root, info: ResolveInfo, **kwargs):
        qs = resolve_partnership_tiers(info)
        return create_connection_slice(qs, info, kwargs, PartnershipTierCountableConnection)

    @staticmethod
    def resolve_business(_root, info: ResolveInfo, *, id=None, slug=None):
        return resolve_business(info, id=id, slug=slug)

    @staticmethod
    def resolve_businesses(_root, info: ResolveInfo, **kwargs):
        qs = resolve_businesses(info)
        return create_connection_slice(qs, info, kwargs, BusinessCountableConnection)

    @staticmethod
    def resolve_business_by_user(_root, info: ResolveInfo):
        return resolve_business_by_user(info)

    @staticmethod
    def resolve_tier_pricings(
        _root, info: ResolveInfo, *, tier_id=None, variant_id=None, **kwargs
    ):
        qs = resolve_tier_pricings(info, tier_id=tier_id, variant_id=variant_id)
        return create_connection_slice(qs, info, kwargs, TierPricingCountableConnection)

    @staticmethod
    def resolve_business_orders(_root, info: ResolveInfo, *, business_id=None, **kwargs):
        qs = resolve_business_orders(info, business_id=business_id)
        return create_connection_slice(qs, info, kwargs, BusinessOrderCountableConnection)


class B2BMutations(graphene.ObjectType):
    # Partnership Tier mutations
    partnership_tier_create = PartnershipTierCreate.Field()
    partnership_tier_update = PartnershipTierUpdate.Field()
    partnership_tier_delete = PartnershipTierDelete.Field()

    # Business mutations
    business_create = BusinessCreate.Field()
    business_update = BusinessUpdate.Field()
    business_delete = BusinessDelete.Field()
    business_verify = BusinessVerify.Field()

    # Business User mutations
    business_user_create = BusinessUserCreate.Field()
    business_user_update = BusinessUserUpdate.Field()
    business_user_delete = BusinessUserDelete.Field()

    # Tier Pricing mutations
    tier_pricing_bulk_create = TierPricingBulkCreate.Field()
    tier_pricing_delete = TierPricingDelete.Field()
