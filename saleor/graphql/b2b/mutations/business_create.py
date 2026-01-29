import graphene
from django.utils.text import slugify

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...account.types import AddressInput
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelMutation
from ...core.types import BaseInputObjectType, NonNullList
from ...meta.inputs import MetadataInput
from ..types import Business
from .utils import B2BError


class BusinessInput(BaseInputObjectType):
    name = graphene.String(description="Name of the business.")
    slug = graphene.String(description="Slug of the business.")
    tax_id = graphene.String(description="Business tax ID / VAT number.")
    company_registration_number = graphene.String(
        description="Company registration number."
    )
    tier_id = graphene.ID(description="ID of the partnership tier.")
    billing_address = AddressInput(description="Billing address.")
    email = graphene.String(description="Contact email.")
    phone = graphene.String(description="Contact phone number.")
    website = graphene.String(description="Business website URL.")
    note = graphene.String(description="Internal notes about the business.")
    is_active = graphene.Boolean(description="Whether the business is active.")
    metadata = NonNullList(MetadataInput, description="Business metadata.")
    private_metadata = NonNullList(
        MetadataInput, description="Business private metadata."
    )

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class BusinessCreateInput(BusinessInput):
    name = graphene.String(description="Name of the business.", required=True)
    tax_id = graphene.String(
        description="Business tax ID / VAT number.", required=True
    )
    tier_id = graphene.ID(description="ID of the partnership tier.", required=True)

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class BusinessCreate(ModelMutation):
    class Arguments:
        input = BusinessCreateInput(
            required=True, description="Fields required to create a business."
        )

    class Meta:
        description = "Creates a new B2B business."
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

        # Auto-generate slug if not provided
        if "name" in cleaned_input and "slug" not in cleaned_input:
            cleaned_input["slug"] = slugify(cleaned_input["name"])
        elif "slug" in cleaned_input:
            cleaned_input["slug"] = slugify(cleaned_input["slug"])

        # Handle tier
        if "tier_id" in cleaned_input:
            from ...core.utils import from_global_id_or_error

            _, tier_pk = from_global_id_or_error(
                cleaned_input.pop("tier_id"), "PartnershipTier"
            )
            cleaned_input["tier_id"] = tier_pk

        # Handle billing address
        if billing_address := cleaned_input.pop("billing_address", None):
            from ....account.models import Address

            address = Address.objects.create(**billing_address)
            cleaned_input["billing_address"] = address

        return cleaned_input
