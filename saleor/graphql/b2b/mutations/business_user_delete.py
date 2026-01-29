import graphene

from ....b2b import BusinessUserRole, models
from ....permission.enums import B2BPermissions
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelDeleteMutation
from ..types import BusinessUser
from .utils import B2BError


class BusinessUserDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the business user.")

    class Meta:
        description = (
            "Removes a user from a B2B business. "
            "Note: Cannot remove the last owner of a business."
        )
        model = models.BusinessUser
        object_type = BusinessUser
        permissions = (B2BPermissions.MANAGE_BUSINESSES,)
        error_type_class = B2BError
        error_type_field = "b2b_errors"
        doc_category = DOC_CATEGORY_B2B

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        from ...core.utils import from_global_id_or_error

        instance_id = data.get("id")
        _, pk = from_global_id_or_error(instance_id, "BusinessUser")
        instance = models.BusinessUser.objects.get(pk=pk)

        # Check if this is the last owner
        if instance.role == BusinessUserRole.OWNER:
            owner_count = models.BusinessUser.objects.filter(
                business=instance.business, role=BusinessUserRole.OWNER
            ).count()
            if owner_count <= 1:
                raise ValueError("Cannot remove the last owner of a business.")

        return super().perform_mutation(_root, info, **data)
