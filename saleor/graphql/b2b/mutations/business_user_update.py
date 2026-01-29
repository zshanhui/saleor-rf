import graphene

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelMutation
from ..types import BusinessUser
from .business_user_create import BusinessUserInput
from .utils import B2BError


class BusinessUserUpdateInput(BusinessUserInput):
    class Meta:
        doc_category = DOC_CATEGORY_B2B


class BusinessUserUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the business user.")
        input = BusinessUserUpdateInput(required=True, description="Fields to update.")

    class Meta:
        description = "Updates a user's membership in a B2B business."
        model = models.BusinessUser
        object_type = BusinessUser
        permissions = (B2BPermissions.MANAGE_BUSINESSES,)
        error_type_class = B2BError
        error_type_field = "b2b_errors"
        doc_category = DOC_CATEGORY_B2B

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)

        # Handle spending limit
        if "spending_limit" in cleaned_input:
            cleaned_input["spending_limit_amount"] = cleaned_input.pop("spending_limit")

        return cleaned_input
