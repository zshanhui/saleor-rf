import graphene

from ...b2b import BusinessUserRole, BusinessVerificationStatus, PartnershipTierType
from ...b2b.enums import CreditOrderStatus
from ..core.doc_category import DOC_CATEGORY_B2B
from ..core.utils import str_to_enum


class BusinessUserRoleEnum(graphene.Enum):
    OWNER = BusinessUserRole.OWNER
    ADMIN = BusinessUserRole.ADMIN
    BUYER = BusinessUserRole.BUYER
    VIEWER = BusinessUserRole.VIEWER

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class BusinessVerificationStatusEnum(graphene.Enum):
    PENDING = BusinessVerificationStatus.PENDING
    IN_REVIEW = BusinessVerificationStatus.IN_REVIEW
    VERIFIED = BusinessVerificationStatus.VERIFIED
    REJECTED = BusinessVerificationStatus.REJECTED

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class PartnershipTierTypeEnum(graphene.Enum):
    BRONZE = PartnershipTierType.BRONZE
    SILVER = PartnershipTierType.SILVER
    GOLD = PartnershipTierType.GOLD
    PLATINUM = PartnershipTierType.PLATINUM
    CUSTOM = PartnershipTierType.CUSTOM

    class Meta:
        doc_category = DOC_CATEGORY_B2B


class CreditOrderStatusEnum(graphene.Enum):
    PENDING = CreditOrderStatus.PENDING
    APPROVED = CreditOrderStatus.APPROVED
    PAID = CreditOrderStatus.PAID
    OVERDUE = CreditOrderStatus.OVERDUE
    CANCELLED = CreditOrderStatus.CANCELLED

    class Meta:
        doc_category = DOC_CATEGORY_B2B


B2BErrorCode = graphene.Enum.from_enum(
    str_to_enum(
        "B2BErrorCode",
        [
            "BUSINESS_NOT_FOUND",
            "BUSINESS_ALREADY_EXISTS",
            "BUSINESS_NOT_ACTIVE",
            "BUSINESS_NOT_VERIFIED",
            "INVALID_TAX_ID",
            "DUPLICATE_TAX_ID",
            "TIER_NOT_FOUND",
            "TIER_ALREADY_EXISTS",
            "INVALID_TIER_CONFIGURATION",
            "USER_ALREADY_MEMBER",
            "USER_NOT_MEMBER",
            "INVALID_ROLE",
            "CANNOT_REMOVE_OWNER",
            "INSUFFICIENT_PERMISSIONS",
            "MINIMUM_ORDER_NOT_MET",
            "MINIMUM_QUANTITY_NOT_MET",
            "CREDIT_LIMIT_EXCEEDED",
            "SPENDING_LIMIT_EXCEEDED",
            "ORDER_APPROVAL_REQUIRED",
            "TIER_PRICING_NOT_FOUND",
            "INVALID_PRICING_CONFIGURATION",
            "GRAPHQL_ERROR",
            "INVALID",
            "NOT_FOUND",
            "REQUIRED",
            "UNIQUE",
        ],
    )
)
