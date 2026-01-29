import graphene

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import BaseMutation
from ...core.types import BaseInputObjectType, NonNullList
from ..types import TierPricing
from .utils import B2BError


class TierPricingInput(BaseInputObjectType):
    tier_id = graphene.ID(required=True, description="ID of the partnership tier.")
    variant_id = graphene.ID(required=True, description="ID of the product variant.")
    channel_id = graphene.ID(required=True, description="ID of the channel.")
    price = graphene.Decimal(required=True, description="The tier price.")
    currency = graphene.String(required=True, description="Currency code.")
    minimum_quantity = graphene.Int(
        default_value=1, description="Minimum quantity to qualify for this price."
    )

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class TierPricingBulkCreate(BaseMutation):
    tier_pricings = NonNullList(
        TierPricing, description="List of created tier pricings."
    )
    count = graphene.Int(description="Number of tier pricings created.")

    class Arguments:
        input = NonNullList(
            TierPricingInput,
            required=True,
            description="List of tier pricing inputs.",
        )

    class Meta:
        description = "Creates or updates tier-specific pricing for product variants."
        permissions = (B2BPermissions.MANAGE_PARTNERSHIP_TIERS,)
        error_type_class = B2BError
        error_type_field = "b2b_errors"
        doc_category = DOC_CATEGORY_B2B

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        from ...core.utils import from_global_id_or_error

        input_list = data.get("input", [])
        created_pricings = []

        for pricing_input in input_list:
            # Resolve IDs
            _, tier_pk = from_global_id_or_error(
                pricing_input["tier_id"], "PartnershipTier"
            )
            _, variant_pk = from_global_id_or_error(
                pricing_input["variant_id"], "ProductVariant"
            )
            _, channel_pk = from_global_id_or_error(
                pricing_input["channel_id"], "Channel"
            )

            # Create or update tier pricing
            tier_pricing, _ = models.TierPricing.objects.update_or_create(
                tier_id=tier_pk,
                variant_id=variant_pk,
                channel_id=channel_pk,
                minimum_quantity=pricing_input.get("minimum_quantity", 1),
                defaults={
                    "price_amount": pricing_input["price"],
                    "currency": pricing_input["currency"],
                },
            )
            created_pricings.append(tier_pricing)

        return TierPricingBulkCreate(
            tier_pricings=created_pricings, count=len(created_pricings)
        )
