class BusinessUserRole:
    """Roles for users within a business organization."""

    OWNER = "owner"
    ADMIN = "admin"
    BUYER = "buyer"
    VIEWER = "viewer"

    CHOICES = [
        (OWNER, "Owner - Full access and ownership"),
        (ADMIN, "Admin - Manage business settings and users"),
        (BUYER, "Buyer - Can place orders"),
        (VIEWER, "Viewer - Read-only access"),
    ]


class BusinessVerificationStatus:
    """Status of business verification process."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    VERIFIED = "verified"
    REJECTED = "rejected"

    CHOICES = [
        (PENDING, "Pending - Awaiting review"),
        (IN_REVIEW, "In Review - Currently being reviewed"),
        (VERIFIED, "Verified - Business has been verified"),
        (REJECTED, "Rejected - Verification rejected"),
    ]


class PartnershipTierType:
    """Default partnership tier types."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    CUSTOM = "custom"

    CHOICES = [
        (BRONZE, "Bronze"),
        (SILVER, "Silver"),
        (GOLD, "Gold"),
        (PLATINUM, "Platinum"),
        (CUSTOM, "Custom"),
    ]


class CreditOrderStatus:
    """Status of credit-based orders."""

    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

    CHOICES = [
        (PENDING, "Pending - Awaiting payment"),
        (APPROVED, "Approved - Credit approved"),
        (PAID, "Paid - Payment received"),
        (OVERDUE, "Overdue - Payment past due date"),
        (CANCELLED, "Cancelled - Order cancelled"),
    ]
