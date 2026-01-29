import graphene

from ...core.doc_category import DOC_CATEGORY_B2B
from ..enums import B2BErrorCode


class B2BError(graphene.ObjectType):
    """Represents errors in B2B operations."""

    field = graphene.String(description="Name of a field that caused the error.")
    message = graphene.String(description="The error message.")
    code = B2BErrorCode(description="The error code.", required=True)

    class Meta:
        doc_category = DOC_CATEGORY_B2B
