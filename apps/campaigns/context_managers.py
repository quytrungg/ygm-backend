from typing import TYPE_CHECKING, Type

from django.template import engines
from django.utils.timezone import now
from django.utils.translation import gettext as _

from apps.campaigns.constants import NoteType
from apps.campaigns.utils import get_chamber_url

django_engine = engines["django"]

if TYPE_CHECKING:
    from apps.campaigns.models import Note
    from apps.incentives.models import Reward
    from apps.members.models import Contract, Invoice


class BaseNoteContextManager:
    """Base class for note context managers."""

    base_context_vars = {
        "DATE": _("Current Date"),
        "YEAR": _("Current Year"),
        "CHAMBER_NAME": _("Chamber Name"),
        "CHAMBER_ADDRESS": _("Chamber Address"),
        "CHAMBER_CITY": _("Chamber City"),
        "CHAMBER_STATE": _("Chamber State"),
        "CHAMBER_ZIP": _("Chamber ZIP"),
        "CHAMBER_TRC_PHONE": _("Chamber TRC Phone"),
    }
    context_vars = {}
    default_template_path = "notes/default.html"

    def __init__(self, note, **kwargs) -> None:
        self.note: "Note" = note

    @classmethod
    def get_default_template(cls) -> str:
        """Return default template string if exist."""
        if cls.default_template_path is None:
            return ""
        default_template = django_engine.get_template(
            cls.default_template_path,
        )
        return default_template.template.source

    @classmethod
    def get_context_info(cls) -> dict[str, str]:
        """Return context info."""
        return cls.base_context_vars | cls.context_vars

    def get_base_context(self) -> dict:
        """Fetch context for rendering."""
        datetime = now()
        return {
            "DATE": datetime.strftime("%m/%d/%Y"),
            "YEAR": datetime.strftime("%Y"),
            "CHAMBER_NAME": self.note.campaign.chamber.name,
            "CHAMBER_ADDRESS": self.note.campaign.chamber.address,
            "CHAMBER_CITY": self.note.campaign.chamber.city,
            "CHAMBER_STATE": self.note.campaign.chamber.state,
            "CHAMBER_ZIP": self.note.campaign.chamber.zipcode,
            "CHAMBER_TRC_PHONE": (
                self.note.campaign.chamber.trc_coord_office_phone
            ),
        }

    def get_context(self):
        """Return context map."""
        return self.get_base_context()

    def get_template(self):
        """Return template from note's body."""
        return django_engine.from_string(self.note.body)

    def render_template(self):
        """Render template with values."""
        return self.get_template().render(self.get_context())


class ContractContextManger(BaseNoteContextManager):
    """Contract context manager."""

    context_vars = {
        "CONTRACT_NAME": _("Contract Name"),
        "CONTRACT_URL": _("Contract's public URL"),
        "VOLUNTEER_NAME": _("Volunteer's name."),
    }
    default_template_path = "members/contract_note.html"

    def __init__(self, note, **kwargs) -> None:
        super().__init__(note, **kwargs)
        self.contract: "Contract" = kwargs.get("contract")

    def get_contract_public_url(self) -> str:
        """Return the contract's public url."""
        chamber_url = get_chamber_url(
            self.contract.campaign.chamber,
        )
        return f"{chamber_url}/contract-sign?token={self.contract.token}"

    def get_context(self):
        context = {
            "CONTRACT_NAME": self.contract.name,
            "CONTRACT_URL": self.get_contract_public_url(),
            "VOLUNTEER_NAME": self.contract.created_by.full_name,
        }
        base_context = super().get_context()
        return context | base_context


class InvoiceContextManager(BaseNoteContextManager):
    """Invoice context manager."""

    context_vars = {
        "INVOICE_NUMBER": _("Invoice Number"),
        "INVOICE_NAME": _("Invoice Name"),
        "INVOICE_DETAIL": _("Table with purchased levels."),
        "MEMBER_PK": _("Member PK"),
        "MEMBER_NAME": _("Member Name"),
        "MEMBER_FIRST_NAME": _("Member First Name"),
        "MEMBER_LAST_NAME": _("Member Last Name"),
        "MEMBER_ADDRESS": _("Member Address"),
        "MEMBER_CITY": _("Member City"),
        "MEMBER_STATE": _("Member State"),
        "MEMBER_ZIP": _("Member Zip"),
    }
    default_template_path = "members/invoice_note.html"

    def __init__(self, note, **kwargs) -> None:
        super().__init__(note, **kwargs)
        self.invoice: "Invoice" = kwargs.get("invoice")

    def get_invoice_detail(self):
        """Invoice table."""
        data = {
            "created_date": self.invoice.created.date().strftime("%m/%d/%Y"),
            "levels": self.invoice.contract.levels.all(),
        }
        return django_engine.get_template(
            "members/invoice_table.html",
        ).render(data)

    def get_context(self):
        context = {
            "INVOICE_NUMBER": self.invoice.pk,
            "INVOICE_NAME": self.invoice.name,
            "INVOICE_DETAIL": self.get_invoice_detail(),
            "MEMBER_PK": self.invoice.contract.member.pk,
            "MEMBER_NAME": self.invoice.contract.member.name,
            "MEMBER_FIRST_NAME": self.invoice.contract.member.first_name,
            "MEMBER_LAST_NAME": self.invoice.contract.member.last_name,
            "MEMBER_ADDRESS": self.invoice.contract.member.address,
            "MEMBER_CITY": self.invoice.contract.member.city,
            "MEMBER_STATE": self.invoice.contract.member.state,
            "MEMBER_ZIP": self.invoice.contract.member.zipcode,
        }
        base_context = super().get_context()
        return context | base_context


class RewardContextManager(BaseNoteContextManager):
    """Provide context for reward notes."""

    context_vars = {
        "INCENTIVE_NAME": _("Incentive Name"),
        "INCENTIVE_THRESHOLD": _("Incentive Threshold"),
        "INCENTIVE_TYPE": _("Incentive Type"),
        "INCENTIVE_VALUE": _("Incentive Value"),
    }
    default_template_path = "incentives/reward_note.html"

    def __init__(self, note, **kwargs):
        super().__init__(note, **kwargs)
        self.reward: "Reward" = kwargs.get("reward")

    def get_context(self):
        context = {
            "INCENTIVE_NAME": self.reward.incentive.name,
            "INCENTIVE_THRESHOLD": self.reward.incentive.threshold,
            "INCENTIVE_TYPE": self.reward.incentive.type,
            "INCENTIVE_VALUE": self.reward.incentive.value,
        }
        base_context = super().get_context()
        return context | base_context


note_context_manager_map: dict[any, Type[BaseNoteContextManager]] = {
    NoteType.CONTRACT_NOTE.value: ContractContextManger,
    NoteType.INVOICE_NOTE.value: InvoiceContextManager,
    NoteType.THANKYOU_LETTER.value: BaseNoteContextManager,
    NoteType.PE_THANKYOU_LETTER.value: BaseNoteContextManager,
    NoteType.COMPANY_THANKYOU_LETTER.value: BaseNoteContextManager,
    NoteType.REWARD_EMAIL.value: RewardContextManager,
    NoteType.RENEWAL_LETTER.value: BaseNoteContextManager,
    NoteType.RENEWAL_CONTRACT.value: BaseNoteContextManager,
}


def get_context_manager(note_type: str) -> type[BaseNoteContextManager]:
    """Return context manager for selected note."""
    return note_context_manager_map.get(
        note_type,
        BaseNoteContextManager,
    )
