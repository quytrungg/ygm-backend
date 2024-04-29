import re
from decimal import Decimal
from typing import Iterable

from django.db.backends.mysql.base import CursorWrapper
from django.db.models import OuterRef, Q, Subquery
from django.utils import timezone

from apps.campaigns.constants import UserCampaignRole
from apps.campaigns.models import Campaign, Level, LevelInstance, UserCampaign
from apps.chambers.models import Chamber, StoredMember, StoredMemberContact
from apps.historical_data.services import ContractData
from apps.members.constants import ContractStatus, ContractType
from apps.members.models import Contract, ContractCreditInfo, Member

CONTRACT_FETCH_SQL_TEMPLATE = """
SELECT
    id,
    chamber,
    contract_type,
    sponsorship,
    company,
    company_name,
    company_addr1,
    company_city,
    company_state,
    company_zip,
    company_fax,
    contact,
    contact_first,
    contact_last,
    contact_phone,
    contact_cellphone,
    contact_email,
    sale_cost,
    preference_date,
    additional_desc,
    e_signature,
    volunteer_name
FROM contracts
WHERE company = -1 and chamber in ({first_list_of_ids})
union
SELECT
    contracts.id,
    contracts.chamber,
    contracts.contract_type,
    contracts.sponsorship,
    contracts.company,
    companies.name,
    companies.addr1,
    companies.city,
    companies.state,
    companies.zip,
    companies.fax,
    contracts.contact,
    contracts.contact_first,
    contracts.contact_last,
    contracts.contact_phone,
    contracts.contact_cellphone,
    contracts.contact_email,
    contracts.sale_cost,
    contracts.preference_date,
    contracts.additional_desc,
    contracts.e_signature,
    contracts.volunteer_name
FROM contracts, companies
WHERE contracts.company = companies.id and
contracts.company != -1 and
contracts.chamber in ({second_list_of_ids})
"""


def fetch_contract_data(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
) -> list[ContractData]:
    """Select contracts from old db."""
    query = CONTRACT_FETCH_SQL_TEMPLATE.format(
        first_list_of_ids=", ".join(["%s" for _ in old_campaign_ids]),
        second_list_of_ids=", ".join(["%s" for _ in old_campaign_ids]),
    )
    cursor.execute(query, tuple(old_campaign_ids) + tuple(old_campaign_ids))
    raw_contracts = cursor.fetchall()
    contracts: list[ContractData] = [
        ContractData(
            id=contract[0],
            chamber=contract[1],
            type=contract[2],
            sponsorship=contract[3],
            stored_member=contract[4],
            member_name=contract[5],
            member_address=contract[6],
            member_city=contract[7],
            member_state=contract[8],
            member_zipcode=contract[9],
            member_phone=contract[10],
            contact=contract[11],
            contact_first_name=contract[12],
            contact_last_name=contract[13],
            contact_work_phone=contract[14],
            contact_mobile_phone=contract[15],
            contact_email=contract[16],
            cost=(
                Decimal(re.sub(r"\D+", "", contract[17]) or 0)
                if contract[17] else Decimal(0)
            ),
            created_date=contract[18],
            note=contract[19],
            signature=contract[20],
            volunteer_name=contract[21],
        ) for contract in raw_contracts
    ]
    return contracts


def create_new_credit_instance(contract: ContractData) -> ContractCreditInfo:
    """Return new ContractCreditInfo instance."""
    return ContractCreditInfo(
        contract=contract,
        user_campaign=contract.created_by,
        portion=Decimal(1),
    )


def create_new_contract_instance(
    new_members_map: dict[int, int],
    contract_type_map: dict[int, str],
    contract: ContractData,
    campaign_id: int,
    user_campaign: int,
) -> Contract:
    """Return new Contract instance."""
    return Contract(
        name=f"{contract.member_name or 'Contract'} {contract.created_date}",
        type=contract_type_map.get(contract.type),
        status=ContractStatus.APPROVED,
        note=contract.note or "",
        approved_at=timezone.now(),
        created_by=user_campaign,
        member=new_members_map[contract.id],
        campaign_id=campaign_id,
        signature=contract.signature or "",
        signed_at=timezone.now() if contract.signature else None,
        is_renewed=False,
        external_id=contract.id,
    )


def create_new_user_campaign_instance(
    contract: ContractData,
    campaign_id: int,
) -> UserCampaign:
    """Return new UserCampaign instance."""
    return UserCampaign(
        first_name=contract.volunteer_name,
        last_name=contract.volunteer_name,
        campaign_id=campaign_id,
        role=UserCampaignRole.VOLUNTEER,
    )


def create_new_contact_instance(
    contract: ContractData,
    stored_member_id: int,
) -> StoredMemberContact:
    """Return new StoredMemberContact instance."""
    return StoredMemberContact(
        first_name=contract.contact_first_name or f"First Name {contract.id}",
        last_name=contract.contact_last_name or f"Last Name {contract.id}",
        email=contract.contact_email,
        work_phone=contract.contact_work_phone or "",
        mobile_phone=contract.contact_mobile_phone or "",
        stored_member_id=stored_member_id,
        external_id=contract.contact,
    )


def create_new_member_instance(
    contract: ContractData,
    stored_member_id: int,
) -> Member:
    """Return new Member instance."""
    return Member(
        name=contract.member_name or f"Member {contract.id}",
        address=contract.member_address or "",
        city=contract.member_city or "",
        state=contract.member_state[:2] if contract.member_state else "",
        zipcode=contract.member_zipcode[:5] if contract.member_zipcode else "",
        phone=contract.member_phone or "",
        email=contract.contact_email or "",
        first_name=contract.contact_first_name or "",
        last_name=contract.contact_last_name or "",
        work_phone=contract.contact_work_phone or "",
        mobile_phone=contract.contact_mobile_phone or "",
        stored_member_id=stored_member_id,
    )


def get_user_campaign_id(
    campaign_id,
    volunteer_name,
) -> int:
    """Return user campaign id value for each campaign id key."""
    try:
        first_name, last_name = volunteer_name.split()
        query = (
            Q(first_name__iexact=first_name, last_name__iexact=last_name) |
            Q(first_name__iexact=last_name, last_name__iexact=first_name)
        )
    except ValueError:
        query = (
            Q(first_name__iexact=volunteer_name) |
            Q(last_name__iexact=volunteer_name)
        )
    user_campaign = UserCampaign.objects.filter(
        query,
        campaign_id=campaign_id,
    ).first()

    if not user_campaign:
        user_campaign = UserCampaign.objects.filter(
            campaign_id=campaign_id,
        ).order_by("role").first()
    return user_campaign


def get_level_ids_map() -> dict[int, int]:
    """Return level id value for each external id key."""
    return dict(
        Level.objects.filter(
            external_id__isnull=False,
        ).values_list("external_id", "id"),
    )


def get_stored_member_ids_map(target_chamber: Chamber) -> dict[int, int]:
    """Return stored member id value for each external id key."""
    return dict(
        StoredMember.objects.filter(
            chamber_id=target_chamber.id,
            external_id__isnull=False,
        ).values_list("external_id", "id"),
    )


def get_chamber_campaign_ids_map() -> dict[int, int]:
    """Return latest campaign id value for each chamber external id key."""
    return dict(
        Chamber.objects.filter(external_id__isnull=False).annotate(
            latest_campaign_id=Subquery(
                Campaign.objects.filter(
                    chamber=OuterRef("pk"),
                ).order_by("-id").values("id")[:1],
            ),
        ).values_list("external_id", "latest_campaign_id"),
    )


# pylint: disable=too-many-locals,too-many-statements
def import_contracts(  # noqa: C901
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
    target_chamber: Chamber,
) -> Iterable[int]:
    """Import old contracts data."""
    old_contracts: list[ContractData] = fetch_contract_data(
        cursor=cursor,
        old_campaign_ids=old_campaign_ids,
    )
    new_credits = []
    new_contacts = []
    new_level_instances_map = {}
    new_members_map: dict[int, Member] = {}
    new_contracts_map = {}
    sponsorship_to_campaign_map: dict[int, int] = dict(
        Level.objects.filter(
            product__category__campaign__chamber_id=target_chamber.id,
            external_id__isnull=False,
        ).values_list("external_id", "product__category__campaign_id"),
    )
    stored_member_ids_map = get_stored_member_ids_map(target_chamber)
    level_ids_map = dict(
        Level.objects.filter(
            product__category__campaign__chamber_id=target_chamber.id,
            external_id__isnull=False,
        ).values_list("external_id", "id"),
    )
    old_stored_member_contacts = StoredMemberContact.objects.filter(
        stored_member__chamber_id=target_chamber.id,
        external_id__isnull=False,
    )
    contact_ids_map: dict[int, int] = dict(
        old_stored_member_contacts.values_list("external_id", "id"),
    )
    contact_email_ids_map: dict[int, int] = dict(
        old_stored_member_contacts.values_list("email", "id"),
    )
    contract_type_map = {0: ContractType.TRADE, 1: ContractType.CASH}
    for contract in old_contracts:
        campaign_id = sponsorship_to_campaign_map.get(contract.sponsorship)
        stored_member_id = stored_member_ids_map.get(contract.stored_member)
        if not campaign_id:
            continue
        new_members_map[contract.id] = create_new_member_instance(
            contract,
            stored_member_id,
        )
        if contract.contact_email and stored_member_id and not (
            contact_ids_map.get(contract.contact)
            or contact_email_ids_map.get(contract.contact_email)
        ):
            new_contacts.append(
                create_new_contact_instance(contract, stored_member_id),
            )
        new_level_instances_map[contract.id] = LevelInstance(
            level_id=level_ids_map.get(contract.sponsorship),
            cost=contract.cost,
        )
    Member.objects.bulk_create(new_members_map.values())
    StoredMemberContact.objects.bulk_create(new_contacts)
    for contract in old_contracts:
        campaign_id = sponsorship_to_campaign_map.get(contract.sponsorship)
        stored_member_id = stored_member_ids_map.get(contract.stored_member)
        if not campaign_id:
            continue
        user_campaign = get_user_campaign_id(
            campaign_id,
            contract.volunteer_name,
        )
        new_contracts_map[contract.id] = create_new_contract_instance(
            new_members_map,
            contract_type_map,
            contract,
            campaign_id,
            user_campaign,
        )
    new_contracts = Contract.objects.bulk_create(new_contracts_map.values())
    for old_contract_id, contract in new_contracts_map.items():
        level_instance = new_level_instances_map[old_contract_id]
        level_instance.contract = contract
        new_credits.append(create_new_credit_instance(contract))
    ContractCreditInfo.objects.bulk_create(new_credits)
    LevelInstance.objects.bulk_create(new_level_instances_map.values())
    contracts_to_update = []
    # members_to_update = []
    for new_contract in new_contracts:
        level_instance = new_contract.levels.select_related(
            "level__product",
        ).first()
        if level_instance:
            new_contract.name = (
                f"{level_instance.level.product.name} - "
                f"{new_contract.created_by.first_name} "
                f"{new_contract.created_by.last_name}"
            )
            contracts_to_update.append(new_contract)
        # if new_contract.member.stored_member:
        #     contact = new_contract.member.stored_member.contacts.filter(
        #         email=new_contract.member.email,
        #     ).first()
    #         if contact:
    #             new_contract.member.name = contact.stored_member.name
    #             new_contract.member.address = contact.stored_member.address
    #             new_contract.member.city = contact.stored_member.city
    #             new_contract.member.state = contact.stored_member.state[:2]
    #             new_contract.member.first_name = contact.first_name
    #             new_contract.member.last_name = contact.last_name
    #             new_contract.member.work_phone = contact.work_phone
    #             new_contract.member.mobile_phone = contact.mobile_phone
    #             members_to_update.append(new_contract.member)
    Contract.objects.bulk_update(contracts_to_update, fields=["name"])
    # Member.objects.bulk_update(
    #     members_to_update,
    #     fields=[
    #         "name",
    #         "address",
    #         "city",
    #         "state",
    #         "work_phone",
    #         "mobile_phone",
    #         "first_name",
    #         "last_name",
    #     ],
    # )
    return [contract.id for contract in new_contracts_map.values()]
