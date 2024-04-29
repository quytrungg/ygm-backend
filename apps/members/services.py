import dataclasses
import decimal
from collections import abc
from decimal import Decimal

from django.db import models, transaction
from django.db.models import Prefetch
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.campaigns import models as campaign_models
from apps.chambers import services as chambers_services
from apps.chambers.models import StoredMember
from apps.incentives.services.reward_services import (
    create_new_rewards_for_volunteers,
)

from . import notifications
from .models import Contract, ContractCreditInfo, Invoice, Member


def decline_contract(contract: Contract) -> Contract:
    """Decline contract, its instances and recreate new instances.

    Only decline and restore instances which are not declined yet, because
    when an instance is declined separately, we already restore it.

    """
    with transaction.atomic():
        # Keep this logic in case client wants to use this functionality
        # if contract.is_renewed:
        #     contract.status = Contract.STATUSES.DRAFT
        #     contract.save()
        # else:
        contract.decline()
        contract.levels.filter(
            declined_at__isnull=True,
        ).update(declined_at=timezone.now())
    return contract


def approve_contract(contract: Contract) -> Contract:
    """Approve contract and trigger additional logic."""
    with transaction.atomic():
        contract.approve()
        member: Member = contract.member
        stored_member_data = {
            "chamber": contract.campaign.chamber,
            "name": member.name,
            "address": member.address,
            "city": member.city,
            "state": member.state,
            "zip": member.zipcode,
            "phone": member.phone,
            "contact": {
                "first_name": member.first_name,
                "last_name": member.last_name,
                "work_phone": member.work_phone,
                "mobile_phone": member.mobile_phone,
                "email": member.email,
            },
        }
        _save_member_info_on_contract_approval(
            member_info=stored_member_data,
            chamber_id=contract.campaign.chamber_id,
        )
        invoice_data = {
            "name": contract.name,
            "sent_at": None,
            "is_paid": False,
            "contract": contract,
        }
        Invoice.objects.create(**invoice_data)
        create_new_rewards_for_volunteers(
            campaign_id=contract.campaign_id,
            volunteer_ids=ContractCreditInfo.objects.filter(
                contract_id=contract.id,
            ).values_list("user_campaign_id", flat=True),
        )
    return contract


def _save_member_info_on_contract_approval(member_info: dict, chamber_id: int):
    """Save the member in chamber's stored member list on contract approval."""
    member_contact_info = member_info.pop("contact")
    stored_member, _ = StoredMember.objects.filter(
        chamber_id=chamber_id,
    ).get_or_create(
        name=member_info["name"],
        defaults=member_info,
    )
    chambers_services.add_stored_member_contact(
        stored_member=stored_member,
        contact_info=member_contact_info,
    )


def sign_contract(contract: Contract, data: dict, ip_address: str) -> Contract:
    """Sign to a contract."""
    with transaction.atomic():
        signature = data.get("signature")
        level_ids = data.get("level_ids")
        contract.sign(signature, ip_address)
        contract.levels.exclude(
            id__in=level_ids,
        ).update(declined_at=timezone.now())
    return contract


def delete_contract(contract: Contract) -> Contract:
    """Delete contract and its levels' instances, restore instances.

    Only restore instances which are not declined yet, because
    when an instance is declined separately, we already restore it.

    """
    with transaction.atomic():
        member = contract.member
        contract.delete()
        member.delete()
    return contract


def send_contract(contract_id: int):
    """Send contract to the purchasing member."""
    contract = Contract.objects.filter(
        id=contract_id,
    ).select_related(
        "created_by",
        "campaign__chamber",
    ).first()
    if not contract:
        return
    notifications.ContractEmailNotification(contract).send()


def send_contract_approval_review_email(contract_id: int):
    """Send email to chamber admins to review contract needing approval."""
    contract = Contract.objects.filter(
        id=contract_id,
    ).select_related(
        "campaign__chamber",
    ).first()
    if not contract:
        return
    notifications.ContractApprovalReviewEmailNotification(
        contract=contract,
    ).send()


# pylint: disable=protected-access
def need_send_contract(contract: Contract, is_update: bool) -> bool:
    """Return if contract needs to be sent."""
    if (
        not is_update
        and contract.status == Contract.STATUSES.SENT
    ):
        return True
    if (
        is_update
        and contract._initial_status == Contract.STATUSES.DRAFT
        and contract.status == Contract.STATUSES.SENT
    ):
        return True
    return False


def calculate_total_earnings(campaign: campaign_models.Campaign) -> Decimal:
    """Calculate total earnings from all purchasing members within campaign."""
    if not campaign:
        return Decimal(0)
    return campaign_models.LevelInstance.objects.filter(
        declined_at__isnull=True,
        contract__status=Contract.STATUSES.APPROVED,
        contract__campaign_id=campaign.id,
    ).aggregate(
        total_earnings=Coalesce(models.Sum(models.F("cost")), Decimal(0)),
    )["total_earnings"]


def validate_available_levels(
    level_instances: models.QuerySet[campaign_models.LevelInstance],
) -> dict:
    """Validate available levels in contract, return if errors occur."""
    errors = {}
    level_instances = level_instances.prefetch_related(
        Prefetch(
            "level",
            queryset=campaign_models.Level.objects.all().with_is_available(),
        ),
    )
    for instance in level_instances:
        if not instance.level.is_available:
            errors[f"levels.{instance.index}.level_id"] = _(
                "This product is out of stock",
            )
    return errors


def reassign_contracts(reassign_data: list[dict]) -> None:
    """Reassign contracts to new users and update contract credits info."""
    if not reassign_data:
        return

    contract_list = []
    updated_credits_info = []
    removed_credits_info = []

    for data in reassign_data:
        contract: Contract = data["contract"]
        user = data["user"]
        if contract.created_by_id == user.id:
            continue

        contract_reassignment_result = _reassign_contract(
            contract=contract,
            assignee=user,
            credits_info=contract.credits_info.all(),
        )

        contract_list.append(contract_reassignment_result.contract)
        updated_credits_info.extend(
            contract_reassignment_result.updated_credits_info,
        )
        removed_credits_info.extend(
            contract_reassignment_result.removed_credits_info,
        )
    Contract.objects.bulk_update(contract_list, fields=["created_by"])
    ContractCreditInfo.objects.bulk_update(
        updated_credits_info,
        fields=["user_campaign", "portion"],
    )
    ContractCreditInfo.objects.filter(
        id__in=[credit_info.id for credit_info in removed_credits_info],
    ).delete()


@dataclasses.dataclass
class ContractReassignmentResult:
    """Represent result of contract reassignment action."""

    contract: Contract
    updated_credits_info: abc.Collection[ContractCreditInfo]
    removed_credits_info: abc.Collection[ContractCreditInfo]


def _reassign_contract(
    contract: Contract,
    assignee: campaign_models.UserCampaign,
    credits_info: abc.Collection[ContractCreditInfo],
) -> ContractReassignmentResult:
    """Perform logic to reassign a single contract."""
    old_creator_id = contract.created_by_id
    contract.created_by = assignee
    if contract.is_approved:
        return ContractReassignmentResult(
            contract=contract,
            updated_credits_info=credits_info,
            removed_credits_info=[],
        )

    old_creator_credit = next(
        credit_info
        for credit_info in credits_info
        if credit_info.user_campaign_id == old_creator_id
    )
    is_contract_shared_to_assignee_already = False
    try:
        next(
            credit_info
            for credit_info in credits_info
            if credit_info.user_campaign_id == assignee.id
        )
        is_contract_shared_to_assignee_already = True
    except StopIteration:
        pass

    if is_contract_shared_to_assignee_already:
        updated_credits_info = [
            credit_info
            for credit_info in credits_info
            if credit_info.user_campaign_id != old_creator_id
        ]
        removed_credits_info = [old_creator_credit]
    else:
        old_creator_credit.user_campaign_id = assignee.id
        updated_credits_info = credits_info
        removed_credits_info = []

    credits_count = len(updated_credits_info)
    credited_portion = decimal.Decimal(1) / credits_count
    for credit_info in updated_credits_info:
        credit_info.portion = credited_portion

    return ContractReassignmentResult(
        contract=contract,
        updated_credits_info=updated_credits_info,
        removed_credits_info=removed_credits_info,
    )


def redistribute_contract_credits(contract: Contract):
    """Recalculate portion of contract's value that each user is credited."""
    contract_credits = ContractCreditInfo.objects.filter(
        contract=contract,
    )
    portion_per_credit = Decimal(1) / Decimal(len(contract_credits))
    for contract_credit in contract_credits:
        contract_credit.portion = portion_per_credit
    ContractCreditInfo.objects.bulk_update(
        contract_credits, fields=["portion"],
    )


def set_contract_credits(
    contract: Contract,
    shared_volunteers: list[campaign_models.UserCampaign],
) -> list[ContractCreditInfo]:
    """Set the credits for a contract."""
    credited_volunteers = shared_volunteers
    if contract.created_by not in credited_volunteers:
        credited_volunteers.append(contract.created_by)
    portion = (
        decimal.Decimal(1) / decimal.Decimal(len(credited_volunteers))
    )
    contract.shared_credits_with.clear()
    return ContractCreditInfo.objects.bulk_create(
        ContractCreditInfo(
            user_campaign=volunteer,
            contract=contract,
            portion=portion,
        )
        for volunteer in credited_volunteers
    )


def get_contract_invalid_shared_volunteers(
    contract_creator: campaign_models.UserCampaign,
    shared_volunteers: abc.Collection[campaign_models.UserCampaign],
    contract_stored_member_id: int,
) -> list[campaign_models.UserCampaign]:
    """Return volunteers who the contract shouldn't be shared with."""
    if (
        not contract_stored_member_id
        or contract_creator.member_id != contract_stored_member_id
    ):
        return list(shared_volunteers)

    return [
        shared_volunteer for shared_volunteer in shared_volunteers
        if (
            shared_volunteer.campaign_id != contract_creator.campaign_id
            or shared_volunteer.member_id != contract_stored_member_id
        )
    ]
