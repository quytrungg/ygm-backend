import typing
from decimal import Decimal
from functools import partial

from django.urls import reverse_lazy

from rest_framework import status

import pytest

from apps.core.test_utils import CAAPIClient
from apps.members import factories as mbr_factories
from apps.members import models as mbr_models

from ...tests.conftest import ContractLevelData
from ..utils import calculate_invoice_cost_and_level_count


def get_invoice_url(action: str, kwargs=None) -> typing.Any:
    """Return url of invoice APIs."""
    return reverse_lazy(f"v1:chamber:invoice-{action}", kwargs=kwargs)


list_invoice_url = get_invoice_url(action="list")
detail_invoice_url = partial(get_invoice_url, action="detail")
mark_invoice_paid_url = partial(get_invoice_url, action="pay")
send_invoice_url = partial(get_invoice_url, action="send-invoice")


@pytest.fixture
def member() -> mbr_models.Member:
    """Create a member with email."""
    return mbr_factories.MemberFactory()


@pytest.fixture
def invoice(setup_contract: typing.Callable) -> mbr_models.Invoice:
    """Return a test invoice."""
    contract = setup_contract(
        [
            ContractLevelData(cost=Decimal(100), is_declined=False),
            ContractLevelData(cost=Decimal(200), is_declined=False),
        ],
    )
    return mbr_factories.InvoiceFactory(contract=contract, is_paid=False)


@pytest.fixture
def invoices(setup_contract) -> list[mbr_models.Invoice]:
    """Return list of invoices for test."""
    contract_1 = setup_contract(
        [
            ContractLevelData(cost=Decimal(100), is_declined=False),
            ContractLevelData(cost=Decimal(200), is_declined=False),
        ],
    )
    contract_2 = setup_contract(
        [
            ContractLevelData(cost=Decimal(100), is_declined=True),
            ContractLevelData(cost=Decimal(200), is_declined=False),
        ],
    )
    _invoices = [
        mbr_factories.InvoiceFactory(contract=contract)
        for contract in [contract_1, contract_2]
    ]
    return _invoices


def test_invoice_detail_api(
    chamber_admin_client: CAAPIClient,
    invoice: mbr_models.Invoice,
) -> None:
    """Ensure invoice retrieve api works properly."""
    chamber_admin_client.select_campaign(invoice.contract.campaign)
    response = chamber_admin_client.get(
        detail_invoice_url(kwargs={"pk": invoice.pk}),
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    assert len(response.data["levels"]) == 2
    assert Decimal(response.data["levels"][0]["cost"]) == 100
    assert Decimal(response.data["levels"][1]["cost"]) == 200
    assert response.data["chamber"], response.data["member"]


def test_mark_invoice_paid_api(
    chamber_admin_client: CAAPIClient,
    invoice: mbr_models.Invoice,
) -> None:
    """Ensure mark invoice as paid api works properly."""
    assert not invoice.is_paid
    chamber_admin_client.select_campaign(invoice.contract.campaign)
    response = chamber_admin_client.post(
        mark_invoice_paid_url(kwargs={"pk": invoice.pk}),
    )
    assert response.status_code == status.HTTP_200_OK
    invoice.refresh_from_db()
    assert invoice.is_paid


def test_send_invoice_api(
    chamber_admin_client: CAAPIClient,
    invoice: mbr_models.Invoice,
    member: mbr_models.Member,
    mailoutbox,
) -> None:
    """Ensure send invoice api works properly with status code 200."""
    chamber_admin_client.select_campaign(invoice.contract.campaign)
    response = chamber_admin_client.post(
        send_invoice_url(kwargs={"pk": invoice.pk}),
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.to == [member.email]


def test_invoice_list_api(
    chamber_admin_client: CAAPIClient,
    invoices: list[mbr_models.Invoice],
) -> None:
    """Ensure list of invoices is returned correctly."""
    chamber_admin_client.select_campaign(invoices[0].contract.campaign)
    response = chamber_admin_client.get(list_invoice_url)
    assert response.status_code == status.HTTP_200_OK, response.data
    assert len(response.data["results"]) == len(invoices)
    for invoice_data in response.data["results"]:
        expected = calculate_invoice_cost_and_level_count(invoice_data["id"])
        assert invoice_data["cost"] == expected["cost"]
        assert invoice_data["levels_count"] == expected["levels_count"]
