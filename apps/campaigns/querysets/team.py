import datetime as dt
import decimal

from django.db.models import F, Prefetch, Q, Sum
from django.db.models.functions import Coalesce

from safedelete.queryset import SafeDeleteQueryset

from apps.campaigns import models as campaigns_models
from apps.campaigns.constants import UserCampaignRole
from apps.members.constants import ContractStatus, ContractType


class TeamQuerySet(SafeDeleteQueryset):
    """Provide custom queryset methohds for Team model."""

    def with_team_captain(self):
        """Annotate captain to team."""
        captain_prefetch_obj = Prefetch(
            "members",
            queryset=campaigns_models.UserCampaign.objects.filter(
                role=UserCampaignRole.TEAM_CAPTAIN,
            ),
            to_attr="captain",
        )
        return self.prefetch_related(captain_prefetch_obj)

    def _get_revenue_expr(
        self,
        revenue_from: dt.datetime | None = None,
        revenue_to: dt.datetime | None = None,
        contract_type: str | None = None,
    ):
        """Return the expression to calculate team's generated revenue."""
        credit_path = "members__contracts_credit_info"
        contract_path = f"{credit_path}__contract"
        from_filter = (
            Q(
                **{
                    f"{contract_path}__approved_at__gte": revenue_from,
                },
            )
            if revenue_from else Q()
        )
        to_filter = (
            Q(
                **{
                    f"{contract_path}__approved_at__lte": revenue_to,
                },
            )
            if revenue_to else Q()
        )
        contract_type_filter = (
            Q(**{f"{contract_path}__type": contract_type})
            if contract_type else Q()
        )
        filters = Q(
            **{
                "members__deleted_at__isnull": True,
                f"{contract_path}__status": ContractStatus.APPROVED,
                f"{contract_path}__deleted_at__isnull": True,
                f"{contract_path}__levels__declined_at__isnull": True,
                f"{contract_path}__levels__deleted_at__isnull": True,
            },
        ) & from_filter & to_filter & contract_type_filter
        return Sum(
            (
                F(f"{contract_path}__levels__cost")
                * F(f"{credit_path}__portion")
            ),
            filter=filters,
        )

    def with_total_revenue(self):
        """Annotate team's total generated revenue."""
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

        This relies on time range passed from outside.

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
