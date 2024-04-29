from django.utils.translation import gettext_lazy as _

from libs.notifications.email import (
    DefaultEmailNotification,
    NoteEmailNotification,
)
from libs.notifications.sms import SMSNotification

from apps.campaigns.constants import NoteType
from apps.campaigns.context_managers import (
    ContractContextManger,
    InvoiceContextManager,
)
from apps.campaigns.models.note import Note

from ..campaigns.utils import get_chamber_url
from ..users.models import User
from .models import Contract


class InvoiceEmailNotification(NoteEmailNotification):
    """Used to send invoice email to charged member."""

    def __init__(self, invoice, **template_context):
        super().__init__(**template_context)
        note = Note.objects.get(
            campaign=invoice.contract.campaign,
            type=NoteType.INVOICE_NOTE.value,
        )
        self.context_manager = InvoiceContextManager(
            note,
            invoice=invoice,
        )
        self.invoice = invoice

    def get_formatted_subject(self):
        """Return subject of the email."""
        return _("Invoice Information")

    def get_recipient_list(self) -> list[str]:
        """Return member's email."""
        return [self.invoice.contract.member.email]


class ContractEmailNotification(NoteEmailNotification):
    """Send email about new contract."""

    def __init__(self, contract: Contract, **template_context):
        super().__init__(**template_context)
        note = Note.objects.get(
            campaign=contract.campaign,
            type=NoteType.CONTRACT_NOTE.value,
        )
        self.context_manager = ContractContextManger(
            note,
            contract=contract,
        )
        self.contract = contract

    def get_recipient_list(self):
        """Return purchasing member's email."""
        return [self.contract.member.email]

    def get_formatted_subject(self):
        """Return formatted subject."""
        if not self.contract.is_renewed:
            return _(
                f"{self.contract.campaign.chamber.name} Sponsorship Contract",
            )
        return _(
            f"{self.contract.campaign.chamber.name} Sponsorship Renewals",
        )

    def prepare_mail_args(self) -> dict:
        """Add contract's creator email as CC."""
        mail_args = super().prepare_mail_args()
        mail_args["cc"] = [self.contract.created_by.email]
        return mail_args


class ContractSMSNotification(SMSNotification):
    """Send sms about new contract."""

    def __init__(self, contract: Contract):
        super().__init__()
        self.contract = contract

    def get_contract_public_url(self) -> str:
        """Return the contract's public url."""
        chamber_url = get_chamber_url(
            self.contract.campaign.chamber,
        )
        return f"{chamber_url}/contract-sign?token={self.contract.token}"

    def get_volunteer_name(self) -> str:
        """Format Volunteer full name."""
        volunteer = self.contract.created_by
        return f"{volunteer.first_name} {volunteer.last_name}"

    def get_to_number(self) -> str:
        """Get contract member phone number."""
        return self.contract.member.phone

    def get_body(self) -> str:
        chamber_name = self.contract.campaign.chamber.name
        contract_name = self.contract.name
        return (
            f"Following our discussion, please click the link below to "
            f"sign the {chamber_name} {contract_name} "
            f"Contract: {self.get_contract_public_url()} "
            f"Thanks, {self.get_volunteer_name()}"
        )


class ContractApprovalReviewEmailNotification(DefaultEmailNotification):
    """Send email about contract needing approval review."""

    template = "members/emails/contract_approval_review.html"

    def __init__(self, contract: Contract, **template_context):
        super().__init__(**template_context)
        self.contract = contract
        self.chamber = contract.campaign.chamber
        self.contract_detail_url = (
            f"{get_chamber_url(self.chamber)}/admin/contracts/{contract.id}"
        )

    def get_recipient_list(self) -> list[str]:
        """Return chamber admins' emails."""
        return self.contract.campaign.chamber.users.filter(
            role=User.ROLES.CHAMBER_ADMIN,
        ).values_list("email", flat=True)

    def get_formatted_subject(self) -> str:
        """Return formatted subject."""
        return _("Contract needing approval")

    def get_template_context(self) -> dict:
        """Provide necessary context variables."""
        ctx = super().get_template_context()
        ctx.update(
            contract=self.contract,
            contract_detail_url=self.contract_detail_url,
        )
        return ctx
