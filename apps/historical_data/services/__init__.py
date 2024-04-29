import datetime
from dataclasses import dataclass, field
from decimal import Decimal

from django.conf import settings

import MySQLdb

from apps.core.services import normalize_phone_number


class ConnectionWrapper:
    """Wraps MySQLdb connection."""

    def __init__(self):
        self.connection = None

    def get_connection(self) -> MySQLdb.Connection:
        """Get or create connection."""
        if self.connection is None:
            self.connection = self.connect()
        return self.connection

    @staticmethod
    def connect():
        """Connect to mysql database."""
        return MySQLdb.connect(
            host=settings.OLD_MYSQL_HOST,
            user=settings.OLD_MYSQL_USER,
            password=settings.OLD_MYSQL_PASSWORD,
            database=settings.OLD_MYSQL_DATABASE,
            use_unicode=True,
            charset="utf8mb4",
            ssl_mode="DISABLED",
        )

    def cursor(self):
        """Get cursor."""
        return self.get_connection().cursor()


connection = ConnectionWrapper()


@dataclass
class ChamberSettingsData:
    """DTO for chamber settings."""

    chamber_id: int
    name: str
    value: str


# pylint: disable=too-many-instance-attributes, invalid-name
@dataclass
class ChamberUserData:
    """DTO for chamber users."""

    id: int
    chamber_id: int
    name: str
    first_name: str
    last_name: str
    address: str
    email: str | None
    phone: str

    def updated_email(self, subdomain) -> str:
        """Return unique email for imported user.

        Due to logic mismatch between new and old app, we have to
        enforce that email is unique as old app allows to have multiple users
        with the same email. Some users may not have email, so we provide
        email based on username, chamber id and subdomain.

        We use chamber id from new app, not the old one, that's why it is
        passed from the outside the class.

        """
        if self.email is None:
            return f"{self.name}_{self.id}@{subdomain}.com"
        try:
            name, domain = self.email.split("@")
        except ValueError:
            # In some cases there might be invalid email address,
            # so we just generate it just as if there is no email presented
            self.email = None
            return self.updated_email(subdomain)

        return f"{name}@{domain}"

    def updated_phone(self):
        """Return phone number or default value if phone is not defined."""
        return (
            normalize_phone_number(self.phone)
            if self.phone else "1111111111"
        )


# pylint: disable=invalid-name
@dataclass
class ChamberData:
    """DTO for chambers."""

    id: int
    name: str
    nickname: str
    subdomain: str
    description: str
    created: datetime.date
    logo: str | None = None

    @property
    def formatted_nickname(self):
        """Formatted nickname."""
        return f"old-{self.nickname}"

    @property
    def formatted_subdomain(self):
        """Formatted subdomain."""
        return f"old-{self.subdomain}"

    @property
    def year(self):
        """Return year."""
        return self.created.year


# pylint: disable=too-many-instance-attributes, invalid-name
@dataclass
class CampaignData:
    """DTO for campaign."""

    id: int
    _name: str
    chamber: int
    date: datetime.date
    description: str
    contact: int
    _type: str
    position: int

    @property
    def year(self):
        """Fix year is date is not presented."""
        if self.date is None:
            return datetime.date.today().year
        return self.date.year

    def get_name(self, chamber_name):
        """Fix name if not presented."""
        return self._name or f"Old Campaign from '{chamber_name}'"

    def get_type(self):
        """Fix type if not presented."""
        return self._type or ""


@dataclass
class UserCampaignRelatedInformationData:
    """DTO for campaign-related information of users."""

    id: int
    name: str
    team: int
    chamber: int
    captain: bool
    vice_chair: bool


@dataclass
class TeamData:
    """DTO for teams."""

    id: int
    chamber: int
    name: str
    vice_chair: int
    goal: float


@dataclass
class ResourceData:
    """DTO for resources."""

    id: int
    name: str
    file: str
    file_type: str
    campaign_id: int



@dataclass
class SponsorshipData:
    """DTO for sponsorship."""

    id: int
    chamber: int
    event: int
    name: str
    benefits: str = ""
    multiplier: float = 1
    available: int | None = None
    cost: int | None = None
    position: int | None = None

    def __post_init__(self):
        if self.benefits:
            self.benefits = (
                self.benefits.encode("Windows-1252").decode("UTF-8")
            )


@dataclass
class IncentiveData:
    """DTO for incentives."""

    id: int
    name: str
    threshold: float
    value: float
    type: str
    chamber: int


@dataclass
class RewardData:
    """DTO for paid rewards."""

    id: int
    user: int
    chamber: int
    reward: int


@dataclass
class StoredMemberContactData:
    """DTO for stored member contacts."""

    id: int
    first_name: str
    last_name: str
    email: str = field(default="")
    work_phone: str = field(default="")
    mobile_phone: str = field(default="")

    def __post_init__(self):
        if self.email is None:
            self.email = ""
        self.work_phone = (
            normalize_phone_number(self.work_phone)
            if self.work_phone else "1111111111"
        )
        self.mobile_phone = (
            normalize_phone_number(self.mobile_phone)
            if self.mobile_phone else "1111111111"
        )


@dataclass
class StoredMemberData:
    """DTO for stored members."""

    id: int
    chamber: int
    name: str
    address: str
    address2: str
    city: str
    state: str
    zip: str
    phone: str
    contact: StoredMemberContactData = None

    def __post_init__(self):
        self.phone = normalize_phone_number(self.phone) if self.phone else ""


@dataclass
class ContractData:
    """DTO for contracts."""

    id: int
    chamber: int
    type: int
    sponsorship: int
    stored_member: int
    member_name: str
    member_address: str
    member_city: str
    member_state: str
    member_zipcode: str
    member_phone: str
    contact: int
    contact_first_name: str
    contact_last_name: str
    contact_work_phone: str
    contact_mobile_phone: str
    contact_email: str
    cost: Decimal
    created_date: str
    note: str
    signature: str
    volunteer_name: str

    def __post_init__(self):
        self.member_phone = (
            normalize_phone_number(self.member_phone)
            if self.member_phone else ""
        )
        self.contact_work_phone = (
            normalize_phone_number(self.contact_work_phone)
            if self.contact_work_phone else ""
        )
        self.contact_mobile_phone = (
            normalize_phone_number(self.contact_mobile_phone)
            if self.contact_mobile_phone else ""
        )


@dataclass
class EventTypeData:
    """DTO for Event Type data."""
    id: int | None = None
    chamber: int | None = None
    name: str | None = None


@dataclass
class EventData:
    """DTO for Event data."""
    id: int | None = None
    date: datetime.date | None = None
    name: str | None = None
    description: str | None = None
