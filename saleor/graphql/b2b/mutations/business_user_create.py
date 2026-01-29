import graphene

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelMutation
from ...core.types import BaseInputObjectType
from ..enums import BusinessUserRoleEnum
from ..types import BusinessUser
from .utils import B2BError


class BusinessUserInput(BaseInputObjectType):
    role = BusinessUserRoleEnum(description="Role of the user in the business.")
    can_place_orders = graphene.Boolean(description="Whether the user can place orders.")
    can_view_orders = graphene.Boolean(description="Whether the user can view orders.")
    can_manage_users = graphene.Boolean(
        description="Whether the user can manage other users."
    )
    can_manage_addresses = graphene.Boolean(
        description="Whether the user can manage addresses."
    )
    can_view_credit = graphene.Boolean(
        description="Whether the user can view credit information."
    )
    spending_limit = graphene.Decimal(
        description="Maximum order value this user can place."
    )
    currency = graphene.String(description="Currency for spending limit.")
    is_active = graphene.Boolean(description="Whether the membership is active.")

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class BusinessUserCreateInput(BusinessUserInput):
    business_id = graphene.ID(required=True, description="ID of the business.")
    user_id = graphene.ID(required=True, description="ID of the user.")
    role = BusinessUserRoleEnum(
        required=True, description="Role of the user in the business."
    )

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class BusinessUserCreate(ModelMutation):
    class Arguments:
        input = BusinessUserCreateInput(
            required=True, description="Fields required to create a business user."
        )

    class Meta:
        description = "Adds a user to a B2B business."
        model = models.BusinessUser
        object_type = BusinessUser
        permissions = (B2BPermissions.MANAGE_BUSINESSES,)
        error_type_class = B2BError
        error_type_field = "b2b_errors"
        doc_category = DOC_CATEGORY_B2B

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)

        from ...core.utils import from_global_id_or_error

        # Handle business
        if "business_id" in cleaned_input:
            _, business_pk = from_global_id_or_error(
                cleaned_input.pop("business_id"), "Business"
            )
            cleaned_input["business_id"] = business_pk

        # Handle user
        if "user_id" in cleaned_input:
            _, user_pk = from_global_id_or_error(
                cleaned_input.pop("user_id"), "User"
            )
            cleaned_input["user_id"] = user_pk

        # Handle spending limit
        if "spending_limit" in cleaned_input:
            cleaned_input["spending_limit_amount"] = cleaned_input.pop("spending_limit")

        return cleaned_input
