import graphene
from django.utils.text import slugify

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelMutation
from ..types import Business
from .business_create import BusinessInput
from .utils import B2BError


class BusinessUpdateInput(BusinessInput):
    class Meta:
        doc_category = DOC_CATEGORY_B2B


class BusinessUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the business.")
        input = BusinessUpdateInput(required=True, description="Fields to update.")

    class Meta:
        description = "Updates an existing B2B business."
        model = models.Business
        object_type = Business
        permissions = (B2BPermissions.MANAGE_BUSINESSES,)
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

        # Handle tier
        if "tier_id" in cleaned_input:
            from ...core.utils import from_global_id_or_error

            _, tier_pk = from_global_id_or_error(
                cleaned_input.pop("tier_id"), "PartnershipTier"
            )
            cleaned_input["tier_id"] = tier_pk

        # Handle billing address update
        if billing_address := cleaned_input.pop("billing_address", None):
            if instance.billing_address:
                # Update existing address
                for key, value in billing_address.items():
                    setattr(instance.billing_address, key, value)
                instance.billing_address.save()
            else:
                # Create new address
                from ....account.models import Address

                address = Address.objects.create(**billing_address)
                cleaned_input["billing_address"] = address

        return cleaned_input
