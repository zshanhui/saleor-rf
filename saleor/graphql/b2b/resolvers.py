from ...b2b import models
from ..core import ResolveInfo
from ..core.utils import from_global_id_or_error


def resolve_partnership_tier(info: ResolveInfo, id=None, slug=None):
    """Resolve a single partnership tier by ID or slug."""
    if id:
        _, pk = from_global_id_or_error(id, "PartnershipTier")
        return models.PartnershipTier.objects.filter(pk=pk).first()
    if slug:
        return models.PartnershipTier.objects.filter(slug=slug).first()
    return None


def resolve_partnership_tiers(info: ResolveInfo):
    """Resolve all partnership tiers."""
    return models.PartnershipTier.objects.all()


def resolve_business(info: ResolveInfo, id=None, slug=None):
    """Resolve a single business by ID or slug."""
    if id:
        _, pk = from_global_id_or_error(id, "Business")
        return models.Business.objects.filter(pk=pk).first()
    if slug:
        return models.Business.objects.filter(slug=slug).first()
    return None


def resolve_businesses(info: ResolveInfo):
    """Resolve all businesses."""
    return models.Business.objects.all()


def resolve_business_by_user(info: ResolveInfo):
    """Resolve the business associated with the current user."""
    user = info.context.user
    if not user or not user.is_authenticated:
        return None

    # Get the first active business membership for this user
    membership = (
        models.BusinessUser.objects.filter(user=user, is_active=True)
        .select_related("business")
        .first()
    )
    return membership.business if membership else None


def resolve_business_user(info: ResolveInfo, id):
    """Resolve a single business user by ID."""
    _, pk = from_global_id_or_error(id, "BusinessUser")
    return models.BusinessUser.objects.filter(pk=pk).first()


def resolve_business_users(info: ResolveInfo, business_id=None):
    """Resolve business users, optionally filtered by business."""
    queryset = models.BusinessUser.objects.all()
    if business_id:
        _, pk = from_global_id_or_error(business_id, "Business")
        queryset = queryset.filter(business_id=pk)
    return queryset


def resolve_tier_pricings(info: ResolveInfo, tier_id=None, variant_id=None):
    """Resolve tier pricings with optional filters."""
    queryset = models.TierPricing.objects.all()

    if tier_id:
        _, pk = from_global_id_or_error(tier_id, "PartnershipTier")
        queryset = queryset.filter(tier_id=pk)

    if variant_id:
        _, pk = from_global_id_or_error(variant_id, "ProductVariant")
        queryset = queryset.filter(variant_id=pk)

    return queryset


def resolve_business_orders(info: ResolveInfo, business_id=None):
    """Resolve business orders, optionally filtered by business."""
    queryset = models.BusinessOrder.objects.all()

    if business_id:
        _, pk = from_global_id_or_error(business_id, "Business")
        queryset = queryset.filter(business_id=pk)

    return queryset.select_related("order", "business", "placed_by")
