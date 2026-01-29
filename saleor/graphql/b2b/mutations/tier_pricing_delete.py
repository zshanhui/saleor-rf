import graphene

from ....b2b import models
from ....permission.enums import B2BPermissions
from ...core.doc_category import DOC_CATEGORY_B2B
from ...core.mutations import ModelDeleteMutation
from ..types import TierPricing
from .utils import B2BError


class TierPricingDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of the tier pricing.")

    class Meta:
        description = "Deletes a tier pricing configuration."
        model = models.TierPricing
        object_type = TierPricing
        permissions = (B2BPermissions.MANAGE_PARTNERSHIP_TIERS,)
        error_type_class = B2BError
        error_type_field = "b2b_errors"
        doc_category = DOC_CATEGORY_B2B
