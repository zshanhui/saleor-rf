from decimal import Decimal

import pytest

from ...b2b import BusinessUserRole, BusinessVerificationStatus
from ...b2b.models import Business, BusinessUser, PartnershipTier


@pytest.mark.django_db
class TestPartnershipTier:
    def test_partnership_tier_str(self, partnership_tier_silver):
        # given
        tier = partnership_tier_silver

        # then
        assert str(tier) == "Silver (10.00% discount)"

    def test_partnership_tier_ordering(
        self,
        partnership_tier_bronze,
        partnership_tier_silver,
        partnership_tier_gold,
    ):
        # when
        tiers = list(PartnershipTier.objects.all())

        # then
        # Should be ordered by priority descending, then name
        assert tiers[0] == partnership_tier_gold
        assert tiers[1] == partnership_tier_silver
        assert tiers[2] == partnership_tier_bronze


@pytest.mark.django_db
class TestBusiness:
    def test_business_str(self, business):
        # given/when/then
        assert str(business) == "Test Company Inc."

    def test_business_is_verified(self, business, business_unverified):
        # given/when/then
        assert business.is_verified is True
        assert business_unverified.is_verified is False

    def test_business_available_credit(self, business):
        # given
        business.credit_balance_amount = Decimal("1000.00")
        business.save()

        # when
        available = business.available_credit

        # then
        # Silver tier has 5000 credit limit, balance is 1000
        assert available == Decimal("4000.00")

    def test_business_can_use_credit(self, business):
        # given
        business.credit_balance_amount = Decimal("1000.00")
        business.save()

        # when/then
        assert business.can_use_credit(Decimal("3000.00")) is True
        assert business.can_use_credit(Decimal("5000.00")) is False


@pytest.mark.django_db
class TestBusinessUser:
    def test_business_user_str(self, business_user_owner):
        # given
        user = business_user_owner

        # then
        expected = f"{user.user.email} @ {user.business.name} ({user.role})"
        assert str(user) == expected

    def test_business_user_is_owner(self, business_user_owner, business_user_buyer):
        # given/when/then
        assert business_user_owner.is_owner is True
        assert business_user_buyer.is_owner is False

    def test_business_user_is_admin(self, business_user_owner, business_user_buyer):
        # given/when/then
        assert business_user_owner.is_admin is True
        assert business_user_buyer.is_admin is False

    def test_business_user_can_spend(self, business_user_buyer):
        # given
        user = business_user_buyer
        # Spending limit is 5000

        # when/then
        assert user.can_spend(Decimal("4000.00")) is True
        assert user.can_spend(Decimal("5000.00")) is True
        assert user.can_spend(Decimal("6000.00")) is False

    def test_business_user_permissions_auto_set_owner(self, business, customer_user):
        # given/when
        user = BusinessUser.objects.create(
            business=business,
            user=customer_user,
            role=BusinessUserRole.OWNER,
        )

        # then
        assert user.can_place_orders is True
        assert user.can_view_orders is True
        assert user.can_manage_users is True
        assert user.can_manage_addresses is True
        assert user.can_view_credit is True

    def test_business_user_permissions_auto_set_viewer(self, business, staff_user):
        # given/when
        user = BusinessUser.objects.create(
            business=business,
            user=staff_user,
            role=BusinessUserRole.VIEWER,
        )

        # then
        assert user.can_place_orders is False
        assert user.can_manage_users is False
        assert user.can_manage_addresses is False
