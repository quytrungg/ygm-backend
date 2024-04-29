import datetime as dt
import decimal
import typing

from django.db.models import Case, F, OuterRef, Q, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce

from safedelete.queryset import SafeDeleteQueryset

from apps.members.constants import ContractStatus, ContractType
from apps.users.constants import UserRole

from ..constants import UserCampaignRole


class UserCampaignQuerySet(SafeDeleteQueryset):
    """Provide custom queryset methods for UserCampaign."""

    def with_member_name(self):
        """Annotate member's name if exists."""
        return self.annotate(
            member_name=Coalesce(F("member__name"), Value("")),
        )

    def with_can_sell_contract(self) -> typing.Self:
        """Annotate field to determine if a user campaign can sell contract."""
        return self.annotate(
            can_sell_contract=Case(
                When(
                    Q(role=UserCampaignRole.CHAMBER_CHAIR)
                    | Q(user__role=UserRole.CHAMBER_ADMIN),
                    then=False,
                ),
                default=True,
            ),
        )

    def can_sell_contract(self) -> typing.Self:
        """Exclude users who can not sell contract."""
        return self.with_can_sell_contract().filter(can_sell_contract=True)

    def _get_revenue_expr(
        self,
        revenue_from: dt.datetime | None = None,
        revenue_to: dt.datetime | None = None,
        contract_type: str | None = None,
    ):
        """Return the expression to calculate volunteer's generated revenue."""
        from_filter = (
            Q(contracts_credit_info__contract__approved_at__gte=revenue_from)
            if revenue_from else Q()
        )
        to_filter = (
            Q(contracts_credit_info__contract__approved_at__lte=revenue_to)
            if revenue_to else Q()
        )
        contract_type_filter = (
            Q(contracts_credit_info__contract__type=contract_type)
            if contract_type else Q()
        )
        filters = Q(
            contracts_credit_info__contract__status=ContractStatus.APPROVED,
            contracts_credit_info__contract__deleted_at__isnull=True,
            contracts_credit_info__contract__levels__declined_at__isnull=True,
            contracts_credit_info__contract__levels__deleted_at__isnull=True,
        ) & from_filter & to_filter & contract_type_filter
        return Sum(
            (
                F("contracts_credit_info__contract__levels__cost")
                * F("contracts_credit_info__portion")
            ),
            filter=filters,
        )

    def with_total_revenue(self):
        """Annotate volunteer's total generated revenue."""
        return self.annotate(
            total_revenue=Coalesce(
                self._get_revenue_expr(),
                decimal.Decimal(0),
            ),
        )

    def with_week_revenue(
        self,
        revenue_from: dt.datetime,
        revenue_to: dt.datetime,
    ):
        """Annotate volunteer's total generated revenue in a week.

        This relies on week's time range passed from outside.

        """
        return self.annotate(
            week_revenue=Coalesce(
                self._get_revenue_expr(revenue_from, revenue_to),
                decimal.Decimal(0),
            ),
        )

    def with_total_cash_revenue(self):
        """Annotate volunteer's total generated cash revenue."""
        return self.annotate(
            total_cash_revenue=Coalesce(
                self._get_revenue_expr(contract_type=ContractType.CASH),
                decimal.Decimal(0),
            ),
        )

    def with_total_trade_revenue(self):
        """Annotate volunteer's total generated trade revenue."""
        return self.annotate(
            total_trade_revenue=Coalesce(
                self._get_revenue_expr(contract_type=ContractType.TRADE),
                decimal.Decimal(0),
            ),
        )

    def _get_managed_teams_revenue_expr(
        self,
        revenue_from: dt.datetime | None = None,
        revenue_to: dt.datetime | None = None,
        contract_type: str | None = None,
    ):
        """Return the expr to calculate volunteer's managed teams revenue."""
        contracts_path = (
            "managed_teams__members__contracts_credit_info__contract"
        )
        from_filter = (
            Q(**{f"{contracts_path}__approved_at__gte": revenue_from})
            if revenue_from else Q()
        )
        to_filter = (
            Q(**{f"{contracts_path}__approved_at__lte": revenue_to})
            if revenue_to else Q()
        )
        contract_type_filter = (
            Q(**{f"{contracts_path}__type": contract_type})
            if contract_type else Q()
        )
        return Sum(
            F(f"{contracts_path}__levels__cost")
            * F("managed_teams__members__contracts_credit_info__portion"),
            filter=Q(
                **{
                    f"{contracts_path}__status": ContractStatus.APPROVED,
                    f"{contracts_path}__levels__declined_at__isnull": True,
                    f"{contracts_path}__levels__deleted_at__isnull": True,
                },
            ) & from_filter & to_filter & contract_type_filter,
        )

    def with_managed_teams_total_revenue(self):
        """Annotate user's managed teams' total generated revenue."""
        return self.annotate(
            total_revenue=Coalesce(
                self._get_managed_teams_revenue_expr(),
                decimal.Decimal(0),
            ),
        )

    def with_managed_teams_week_revenue(
        self,
        revenue_from: dt.datetime,
        revenue_to: dt.datetime,
    ):
        """Annotate user's managed teams' week generated revenue."""
        return self.annotate(
            week_revenue=Coalesce(
                self._get_managed_teams_revenue_expr(
                    revenue_from=revenue_from,
                    revenue_to=revenue_to,
                ),
                decimal.Decimal(0),
            ),
        )

    def with_managed_team_total_cash_revenue(self):
        """Annotate user's managed teams' total generated cash revenue."""
        return self.annotate(
            total_cash_revenue=Coalesce(
                self._get_managed_teams_revenue_expr(
                    contract_type=ContractType.CASH,
                ),
                decimal.Decimal(0),
            ),
        )

    # pylint: disable=invalid-name
    def with_week_paid_reward_amount(
        self,
        paid_from: dt.datetime,
        paid_to: dt.datetime,
    ):
        """Annotate amount of rewards paid to volunteer in a week."""
        Reward = self.model._meta.get_field("rewards").related_model
        return self.annotate(
            week_paid_reward_amount=Subquery(
                Reward.objects.filter(
                    user_campaign=OuterRef("pk"),
                    paid_at__gte=paid_from,
                    paid_at__lte=paid_to,
                ).values("user_campaign").annotate(
                    paid_amount=Coalesce(
                        Sum(F("incentive__value")),
                        decimal.Decimal(0),
                    ),
                ).values("paid_amount"),
            ),
        )
