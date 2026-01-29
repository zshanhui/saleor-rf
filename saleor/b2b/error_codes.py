from enum import Enum


class B2BErrorCode(Enum):
    # Business errors
    BUSINESS_NOT_FOUND = "business_not_found"
    BUSINESS_ALREADY_EXISTS = "business_already_exists"
    BUSINESS_NOT_ACTIVE = "business_not_active"
    BUSINESS_NOT_VERIFIED = "business_not_verified"
    INVALID_TAX_ID = "invalid_tax_id"
    DUPLICATE_TAX_ID = "duplicate_tax_id"

    # Partnership tier errors
    TIER_NOT_FOUND = "tier_not_found"
    TIER_ALREADY_EXISTS = "tier_already_exists"
    INVALID_TIER_CONFIGURATION = "invalid_tier_configuration"

    # Business user errors
    USER_ALREADY_MEMBER = "user_already_member"
    USER_NOT_MEMBER = "user_not_member"
    INVALID_ROLE = "invalid_role"
    CANNOT_REMOVE_OWNER = "cannot_remove_owner"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"

    # Order errors
    MINIMUM_ORDER_NOT_MET = "minimum_order_not_met"
    MINIMUM_QUANTITY_NOT_MET = "minimum_quantity_not_met"
    CREDIT_LIMIT_EXCEEDED = "credit_limit_exceeded"
    SPENDING_LIMIT_EXCEEDED = "spending_limit_exceeded"
    ORDER_APPROVAL_REQUIRED = "order_approval_required"

    # Pricing errors
    TIER_PRICING_NOT_FOUND = "tier_pricing_not_found"
    INVALID_PRICING_CONFIGURATION = "invalid_pricing_configuration"

    # General errors
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    REQUIRED = "required"
    UNIQUE = "unique"
