import graphene

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelDeleteMutation
from ..types import Business
from .utils import B2BError


class BusinessDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the business.")

    class Meta:
        description = "Deletes a B2B business."
        model = models.Business
        object_type = Business
        permissions = (B2BPermissions.MANAGE_BUSINESSES,)
        error_type_class = B2BError
        error_type_field = "b2b_errors"
        doc_category = DOC_CATEGORY_B2B
