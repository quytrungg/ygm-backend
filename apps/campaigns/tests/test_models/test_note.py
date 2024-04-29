from typing import TYPE_CHECKING

import pytest

from apps.campaigns.constants import NoteType
from apps.campaigns.context_managers import (
    ContractContextManger,
    InvoiceContextManager,
    RewardContextManager,
)
from apps.campaigns.factories.level_instance import LevelInstanceFactory
from apps.campaigns.models.note import Note
from apps.incentives.factories import IncentiveFactory, RewardFactory
from apps.members.factories.contract import ContractFactory
from apps.members.factories.invoice import InvoiceFactory

if TYPE_CHECKING:
    from apps.campaigns.models import Campaign
    from apps.incentives.models import Reward
    from apps.members.models import Contract, Invoice


@pytest.fixture
def contract(campaign) -> "Contract":
    """Generate campaign contract."""
    _contract = ContractFactory(campaign=campaign)
    LevelInstanceFactory.create_batch(
        size=2,
        contract=_contract,
    )
    return _contract


@pytest.fixture
def invoice(contract) -> "Invoice":
    """Generate contract related invoice."""
    return InvoiceFactory(contract=contract)


@pytest.fixture
def reward(campaign) -> "Reward":
    """Generate reward for volunteer."""
    _incentive = IncentiveFactory(campaign=campaign)
    return RewardFactory(incentive=_incentive)


def test_invoice_note_render(
    campaign: "Campaign",
    invoice: "Invoice",
):
    """Ensure invoice note rendered correctly."""
    note = Note.objects.get(
        campaign=campaign,
        type=NoteType.INVOICE_NOTE.value,
    )
    invoice_context_manger = InvoiceContextManager(
        note=note,
        invoice=invoice,
    )
    rendered_template = invoice_context_manger.render_template()
    assert rendered_template != ""


def test_contract_note_render(
    campaign: "Campaign",
    contract: "Contract",
):
    """Ensure contract note rendered correctly."""
    note = Note.objects.get(
        campaign=campaign,
        type=NoteType.CONTRACT_NOTE.value,
    )
    contract_context_manger = ContractContextManger(
        note=note,
        contract=contract,
    )
    rendered_template = contract_context_manger.render_template()
    assert rendered_template != ""


def test_reward_note_render(
    campaign: "Campaign",
    reward: "Contract",
):
    """Ensure reward note rendered correctly."""
    note = Note.objects.get(
        campaign=campaign,
        type=NoteType.REWARD_EMAIL.value,
    )
    reward_context_manger = RewardContextManager(
        note=note,
        reward=reward,
    )
    rendered_template = reward_context_manger.render_template()
    assert rendered_template != ""
