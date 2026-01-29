import graphene
from django.utils import timezone

from ....b2b import BusinessVerificationStatus, models
from ....permission.enums import B2BPermissions
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import BaseMutation
from ...core.types import BaseInputObjectType
from ..enums import BusinessVerificationStatusEnum
from ..types import Business
from .utils import B2BError


class BusinessVerifyInput(BaseInputObjectType):
    status = BusinessVerificationStatusEnum(
        required=True, description="New verification status."
    )

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class BusinessVerify(BaseMutation):
    business = graphene.Field(Business, description="Updated business.")

    class Arguments:
        id = graphene.ID(required=True, description="ID of the business.")
        input = BusinessVerifyInput(
            required=True, description="Verification status input."
        )

    class Meta:
        description = "Updates the verification status of a B2B business."
        permissions = (B2BPermissions.MANAGE_BUSINESSES,)
        error_type_class = B2BError
        error_type_field = "b2b_errors"
        doc_category = DOC_CATEGORY_B2B

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        from ...core.utils import from_global_id_or_error

        business_id = data.get("id")
        input_data = data.get("input")

        _, business_pk = from_global_id_or_error(business_id, "Business")
        business = models.Business.objects.get(pk=business_pk)

        new_status = input_data["status"]
        business.verification_status = new_status

        if new_status == BusinessVerificationStatus.VERIFIED:
            business.verified_at = timezone.now()
            business.verified_by = info.context.user
        elif new_status == BusinessVerificationStatus.REJECTED:
            business.verified_at = None
            business.verified_by = None

        business.save(
            update_fields=[
                "verification_status",
                "verified_at",
                "verified_by",
                "updated_at",
            ]
        )

        # Create event
        models.BusinessEvent.objects.create(
            business=business,
            type=f"verification_{new_status}",
            user=info.context.user,
            parameters={"previous_status": business.verification_status},
        )

        return BusinessVerify(business=business)
