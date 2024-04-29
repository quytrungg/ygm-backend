import typing
import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from safedelete import SOFT_DELETE
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.core.models import BaseModel

from ..constants import ContractStatus, ContractType
from ..querysets import ContractQuerySet


# pylint: disable=too-many-instance-attributes
class Contract(BaseModel):
    """Represent for contracts in DB.

    Attributes:
        - name (str): Name of the contract.
        - type (str): Contract's type, it could be cash or trade.
        - status (str): Status of the contract.
        - note (str): Note of contract, added by contract creator.
        - approved_at (datetime): the time when contract is approved.
        - created_by (int): UserCampaign id.
        - shared_credits_with: campaign users that are shared in this contract.
        - member (int): Member ID, foreign key to Member model.
        - campaign (int): Campaign ID, foreign key to Campaign model.
        - token (uuid): Token of the contract, used for public info API.
        - signature (str): Contract's signature signed by member.
        - signed_at (datetime): Moment when member signs a contract.

    """

    _safedelete_policy = SOFT_DELETE

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=300,
        editable=False,
    )
    type = models.CharField(
        verbose_name=_("Type"),
        max_length=20,
        choices=ContractType.choices,
        default=ContractType.CASH,
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=ContractStatus.choices,
        default=ContractStatus.DRAFT,
    )
    note = models.CharField(
        verbose_name=_("Private Note"),
        max_length=255,
        blank=True,
    )
    approved_at = models.DateTimeField(
        verbose_name=_("Approved At"),
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        to="campaigns.UserCampaign",
        verbose_name=_("Created By"),
        related_name="created_contracts",
        on_delete=models.CASCADE,
    )
    shared_credits_with = models.ManyToManyField(
        to="campaigns.UserCampaign",
        through="members.ContractCreditInfo",
        verbose_name=_("Shared credits with"),
        related_name="credited_contracts",
        blank=True,
    )
    member = models.ForeignKey(
        to="members.Member",
        verbose_name=_("Member"),
        related_name="contracts",
        on_delete=models.CASCADE,
    )
    campaign = models.ForeignKey(
        to="campaigns.Campaign",
        verbose_name=_("Campaign ID"),
        related_name="contracts",
        on_delete=models.CASCADE,
    )
    token = models.UUIDField(
        verbose_name=_("Token"),
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    signature = models.TextField(
        verbose_name=_("Signature"),
        blank=True,
        default="",
    )
    signed_at = models.DateTimeField(
        verbose_name=_("Signed at"),
        null=True,
        blank=True,
    )
    signer_ip_address = models.CharField(
        max_length=45,
        verbose_name=_("Signer's IP address"),
        blank=True,
    )
    is_renewed = models.BooleanField(
        verbose_name=_("Is Renewed"),
        default=False,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )

    objects = SafeDeleteManager(queryset_class=ContractQuerySet)
    all_objects = SafeDeleteAllManager(queryset_class=ContractQuerySet)
    deleted_objects = SafeDeleteDeletedManager(queryset_class=ContractQuerySet)

    class Meta:
        verbose_name = _("Contract")
        verbose_name_plural = _("Contracts")

    def __str__(self) -> str:
        return self.name

    STATUSES = ContractStatus
    TYPES = ContractType

    def save(self, keep_deleted=False, **kwargs) -> None:
        """Auto set value for `approved_at` field if contract is approved."""
        if self.is_approved and not self.approved_at:
            self.approved_at = timezone.now()
        super().save(keep_deleted, **kwargs)

    @property
    def is_approved(self) -> bool:
        """Check if contract is approved."""
        return self.status == ContractStatus.APPROVED

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_status = self.status

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, campaign, user, member) -> typing.Self:
        """Renew a contract with empty data."""
        self.name = f"{member.name} - Renewal {campaign.year}"
        self.campaign = campaign
        self.status = ContractStatus.DRAFT
        self.created_by = user
        self.member = member
        self.approved_at = None
        self.signature = ""
        self.token = uuid.uuid4()
        self.id = None
        self.is_renewed = True
        return self

    def approve(self):
        """Move contract to approved state."""
        self.status = ContractStatus.APPROVED
        self.approved_at = timezone.now()
        self.save()

    def decline(self):
        """Move contract to declined state."""
        self.status = ContractStatus.DECLINED
        if self.signature or self.signed_at:
            self.signature = ""
            self.signed_at = None
        self.save()

    def sign(self, signature: str, ip_address: str):
        """Set signature and signed_at for contract."""
        self.signature = signature
        self.signed_at = timezone.now()
        self.status = ContractStatus.SIGNED
        self.signer_ip_address = ip_address
        self.save()

    def reassign(self, user) -> typing.Self:
        """Reassign contract's created user and update shared credits info."""
        self.created_by = user
        return self
