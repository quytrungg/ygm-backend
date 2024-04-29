# pylint: disable=too-many-locals,cyclic-import
import typing
from collections import defaultdict

from django.db.models import F, Prefetch
from django.utils import timezone

from apps.campaigns import services as campaigns_services
from apps.campaigns.models import (
    Campaign,
    Level,
    LevelInstance,
    Product,
    ProductAttachment,
    ProductCategory,
    Team,
    UserCampaign,
)
from apps.chambers.models import Chamber, StoredMember, StoredMemberContact
from apps.incentives.models import Incentive, IncentiveQualifier
from apps.members import models as members_models
from apps.timelines import services as timelines_services
from apps.timelines.constants import TimelineTypeChoice
from apps.timelines.models import Timeline, TimelineCategory, TimelineType
from apps.users.models import User


def update_renewal_contract_names(contracts: list) -> list:
    """Update contracts' name during campaign renewal process."""
    contract_names_versions = defaultdict(int)
    for contract in sorted(
        contracts,
        key=lambda obj: obj.signed_at or timezone.now(),
    ):
        contract_name = contract.name
        if contract_name in contract_names_versions:
            contract.name = (
                f"{contract_name} {contract_names_versions.get(contract_name)}"
            )
        contract_names_versions[contract_name] += 1
        contract.signed_at = None
    return contracts


# pylint: disable=unnecessary-comprehension
def renew_campaign_inventory(
    campaign_id: int,
    new_campaign: Campaign,
    **kwargs,
) -> dict[LevelInstance, int]:
    """Renew products and product categories for new campaign."""
    instances_prefetch = Prefetch(
        "instances",
        queryset=LevelInstance.objects.filter(
            declined_at__isnull=True,
            level__product__is_included_in_renewal=True,
        ),
    )
    levels_prefetch = Prefetch(
        "levels",
        queryset=Level.objects.prefetch_related(instances_prefetch),
    )
    product_attachments_prefetch = Prefetch(
        "attachments",
        queryset=ProductAttachment.objects.all(),
    )
    products_prefetch = Prefetch(
        "products",
        queryset=Product.objects.prefetch_related(
            levels_prefetch,
            product_attachments_prefetch,
        ),
    )
    categories = ProductCategory.objects.filter(
        campaign_id=campaign_id,
    ).prefetch_related(products_prefetch)
    renew_categories = []
    renew_products = []
    renew_product_attachments = []
    renew_levels = []
    renew_instances = []
    old_contract_ids = []
    for category in categories:
        products = category.products.all()
        new_category = category.renew(campaign=new_campaign)
        renew_categories.append(new_category)
        for product in products:
            levels = product.levels.all()
            product_attachments = product.attachments.all()
            new_product = product.renew(category=new_category)
            renew_products.append(new_product)
            renew_product_attachments.extend(
                attachment.renew(new_product)
                for attachment in product_attachments
            )
            for level in levels:
                instances = (
                    level.instances.all() if kwargs.get("contracts") else []
                )
                old_contract_ids.extend(
                    instance.contract_id for instance in instances
                )
                new_level = level.renew(product=new_product)
                renew_levels.append(new_level)
                renew_instances.extend(
                    instance.renew(level=new_level) for instance in instances
                )
    ProductCategory.objects.bulk_create(renew_categories)
    Product.objects.bulk_create(renew_products)
    ProductAttachment.objects.bulk_create(renew_product_attachments)
    Level.objects.bulk_create(renew_levels)
    if renew_instances:
        LevelInstance.objects.bulk_create(renew_instances)
    instances_map = {
        instance: contract_id
        for instance, contract_id in zip(renew_instances, old_contract_ids)
    }
    return instances_map


def renew_campaign_incentives(campaign_id: int, new_campaign: Campaign):
    """Renew incentives and their qualifiers for new campaign."""
    incentives = Incentive.objects.filter(
        campaign_id=campaign_id,
    ).prefetch_related(
        Prefetch("qualifiers", queryset=IncentiveQualifier.objects.all()),
    )
    renew_incentives = []
    renew_qualifiers = []
    for incentive in incentives:
        qualifiers = incentive.qualifiers.all()
        new_incentive = incentive.renew(campaign=new_campaign)
        renew_incentives.append(new_incentive)
        renew_qualifiers.extend(
            qualifier.renew(incentive=new_incentive)
            for qualifier in qualifiers
        )
    Incentive.objects.bulk_create(renew_incentives)
    IncentiveQualifier.objects.bulk_create(renew_qualifiers)


def renew_campaign_users_and_contracts(
    campaign_id: int,
    new_campaign: Campaign,
    instances_map: dict[LevelInstance, int],
    **kwargs,
):
    """Renew users for new campaign, clone contracts if it is selected."""
    credits_info_prefetch = Prefetch(
        "credits_info",
        queryset=members_models.ContractCreditInfo.objects.all(),
    )
    instances_prefetch = Prefetch(
        "levels",
        queryset=LevelInstance.objects.filter(contract__isnull=False),
    )
    contracts_prefetch = Prefetch(
        "created_contracts",
        queryset=members_models.Contract.objects.exclude(
            status=members_models.Contract.STATUSES.DECLINED,
        ).prefetch_related(
            instances_prefetch,
            credits_info_prefetch,
        ).select_related("member"),
    )
    users_prefetch = Prefetch(
        "members",
        queryset=UserCampaign.objects.prefetch_related(contracts_prefetch),
    )
    teams = Team.objects.filter(campaign_id=campaign_id).prefetch_related(
        users_prefetch,
    ).annotate(old_id=F("id"))
    users = UserCampaign.objects.filter(
        campaign_id=campaign_id,
    ).prefetch_related(contracts_prefetch).annotate(old_team_id=F("team_id"))
    renew_teams = [team.renew(campaign=new_campaign) for team in teams]
    Team.objects.bulk_create(renew_teams)
    renew_users = []
    renew_contracts = []
    renew_members = []
    old_contract_ids = []
    renew_credits_info = []
    renew_instances = list(instance for instance in instances_map.keys())
    teams_map = {
        team.old_id: new_team.id for team, new_team in zip(teams, renew_teams)
    }
    for user in users:
        contracts = (
            user.created_contracts.all() if kwargs.get("contracts") else []
        )
        new_user = user.renew(campaign=new_campaign)
        renew_users.append(new_user)
        old_contract_ids.extend(contract.id for contract in contracts)
        for contract in contracts:
            credits_info = contract.credits_info.all()
            new_member = contract.member.renew()
            new_contract = contract.renew(
                campaign=new_campaign,
                user=new_user,
                member=new_member,
            )
            renew_members.append(new_member)
            renew_contracts.append(new_contract)
            renew_credits_info.extend(
                credit.renew(contract=new_contract, user_campaign=new_user)
                for credit in credits_info
            )
    UserCampaign.objects.bulk_create(renew_users)
    members_models.Member.objects.bulk_create(renew_members)
    if renew_contracts:
        sorted_contracts = update_renewal_contract_names(renew_contracts)
        members_models.Contract.objects.bulk_create(sorted_contracts)
    members_models.ContractCreditInfo.objects.bulk_create(renew_credits_info)
    contracts_map = {
        old_contract_id: renew_contract.id
        for old_contract_id, renew_contract
        in zip(old_contract_ids, renew_contracts)
    }
    for instance in renew_instances:
        try:
            old_contract_id = instances_map[instance]
            instance.contract_id = contracts_map[old_contract_id]
        except KeyError:
            pass
    users_teams_map = {
        renew_user: user.old_team_id
        for renew_user, user in zip(renew_users, users)
    }
    for user in renew_users:
        try:
            old_team_id = users_teams_map[user]
            user.team_id = teams_map[old_team_id]
        except KeyError:
            pass
    UserCampaign.objects.bulk_update(renew_users, fields=["team_id"])
    LevelInstance.objects.bulk_update(renew_instances, fields=["contract_id"])
    members_models.Contract.objects.filter(
        campaign_id=new_campaign.id,
        levels__isnull=True,
    ).delete()


def renew_chamber_campaign(chamber: Chamber, validated_data: dict) -> int:
    """Implement logic to renew campaign and return new campaign's id."""
    campaign = campaigns_services.get_chamber_newest_campaign(chamber)
    campaign_id = campaign.id
    campaign.renew(name=validated_data["name"], year=validated_data["year"])
    instances_map = {}
    if validated_data.get("inventory"):
        instances_map = renew_campaign_inventory(
            campaign_id,
            campaign,
            **validated_data,
        )
    else:
        campaigns_services.create_default_product_categories(campaign=campaign)
    if validated_data.get("incentives"):
        renew_campaign_incentives(campaign_id, campaign)
    if validated_data.get("users"):
        renew_campaign_users_and_contracts(
            campaign_id,
            campaign,
            instances_map,
            **validated_data,
        )
    else:
        campaigns_services.create_default_user_campaign(campaign=campaign)
    return campaign.id


class StoredMemberContactInfo(typing.TypedDict):
    """Represent basic information of a stored member contact."""

    email: str
    first_name: str
    last_name: str
    work_phone: str
    mobile_phone: str


def add_stored_member_contact(
    stored_member: StoredMember,
    contact_info: StoredMemberContactInfo,
) -> tuple[StoredMemberContact, bool]:
    """Add contact information of a `StoredMember`, update if exists."""
    return StoredMemberContact.objects.update_or_create(
        stored_member=stored_member,
        email=contact_info["email"],
        defaults=contact_info,
    )


def generate_default_timelines(chamber: Chamber) -> None:
    """Generate default timelines for new created chamber."""
    category_map = dict(TimelineCategory.objects.values_list("name", "id"))
    timeline_type_map = dict(TimelineType.objects.values_list("name", "id"))
    chamber_admin = chamber.users.filter(role=User.ROLES.CHAMBER_ADMIN).first()
    tc_csv_data = timelines_services.get_data_from_csv_file(
        "assets/timelines/23OS Timeline TC sample.xlsx - Sheet1.csv",
    )
    vc_csv_data = timelines_services.get_data_from_csv_file(
        "assets/timelines/23OS Timeline VC sample.xlsx - Sheet1.csv",
    )
    tc_timelines = timelines_services.get_timelines_from_csv_data(
        tc_csv_data,
        chamber.id,
        category_map,
        timeline_type_map[TimelineTypeChoice.WITHOUT_VICE_CHAIR],
        chamber_admin.id,
    )
    vc_timelines = timelines_services.get_timelines_from_csv_data(
        vc_csv_data,
        chamber.id,
        category_map,
        timeline_type_map[TimelineTypeChoice.WITH_VICE_CHAIR],
        chamber_admin.id,
    )
    Timeline.objects.bulk_create(tc_timelines + vc_timelines)
