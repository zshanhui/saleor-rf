import graphene
from django.utils.text import slugify

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelMutation
from ...core.types import BaseInputObjectType
from ..types import PartnershipTier
from .partnership_tier_create import PartnershipTierInput
from .utils import B2BError


class PartnershipTierUpdateInput(PartnershipTierInput):
    class Meta:
        doc_category = DOC_CATEGORY_B2B


class PartnershipTierUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the partnership tier.")
        input = PartnershipTierUpdateInput(
            required=True, description="Fields to update."
        )

    class Meta:
        description = "Updates an existing partnership tier."
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

        if "slug" in cleaned_input:
            cleaned_input["slug"] = slugify(cleaned_input["slug"])

        # Map input fields to model fields
        if "minimum_order_value" in cleaned_input:
            cleaned_input["minimum_order_value_amount"] = cleaned_input.pop(
                "minimum_order_value"
            )
        if "credit_limit" in cleaned_input:
            cleaned_input["credit_limit_amount"] = cleaned_input.pop("credit_limit")

        return cleaned_input
