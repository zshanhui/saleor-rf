import graphene
from django.utils.text import slugify

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelMutation
from ...core.types import BaseInputObjectType, NonNullList
from ...meta.inputs import MetadataInput
from ..enums import PartnershipTierTypeEnum
from ..types import PartnershipTier
from .utils import B2BError


class PartnershipTierInput(BaseInputObjectType):
    name = graphene.String(description="Name of the partnership tier.")
    slug = graphene.String(description="Slug of the partnership tier.")
    type = PartnershipTierTypeEnum(description="Type of the partnership tier.")
    description = graphene.String(description="Description of the tier benefits.")
    discount_percentage = graphene.Decimal(
        description="Base discount percentage for this tier."
    )
    minimum_order_quantity = graphene.Int(description="Minimum quantity per order.")
    minimum_order_value = graphene.Decimal(description="Minimum order value required.")
    currency = graphene.String(description="Currency code for monetary values.")
    credit_limit = graphene.Decimal(
        description="Maximum credit limit for businesses in this tier."
    )
    payment_terms_days = graphene.Int(
        description="Number of days for payment terms (0 = prepaid)."
    )
    priority = graphene.Int(
        description="Priority for tier ordering (higher = better tier)."
    )
    is_active = graphene.Boolean(description="Whether the tier is active.")
    metadata = NonNullList(MetadataInput, description="Tier metadata.")
    private_metadata = NonNullList(MetadataInput, description="Tier private metadata.")

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class PartnershipTierCreateInput(PartnershipTierInput):
    name = graphene.String(description="Name of the partnership tier.", required=True)

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class PartnershipTierCreate(ModelMutation):
    class Arguments:
        input = PartnershipTierCreateInput(
            required=True, description="Fields required to create a partnership tier."
        )

    class Meta:
        description = "Creates a new partnership tier."
        model = models.PartnershipTier
        object_type = PartnershipTier
        permissions = (B2BPermissions.MANAGE_PARTNERSHIP_TIERS,)
        error_type_class = B2BError
        error_type_field = "b2b_errors"
        doc_category = DOC_CATEGORY_B2B
        support_meta_field = True
        support_private_meta_field = True

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)

        # Auto-generate slug if not provided
        if "name" in cleaned_input and "slug" not in cleaned_input:
            cleaned_input["slug"] = slugify(cleaned_input["name"])
        elif "slug" in cleaned_input:
            cleaned_input["slug"] = slugify(cleaned_input["slug"])

        # Map input fields to model fields
        if "minimum_order_value" in cleaned_input:
            cleaned_input["minimum_order_value_amount"] = cleaned_input.pop(
                "minimum_order_value"
            )
        if "credit_limit" in cleaned_input:
            cleaned_input["credit_limit_amount"] = cleaned_input.pop("credit_limit")

        return cleaned_input
