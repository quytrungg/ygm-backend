from dataclasses import dataclass

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class CampaignStatus(TextChoices):
    """Provide statuses that occur in a campaign.

    Each campaign will go through these statuses:
        - created: Campaign Created
        - open: Open Renewal
        - live: Go Live
        - done: Mark As Done

    """

    CREATED = "created", _("Campaign Created")
    RENEWAL = "renewal", _("Open Renewal")
    LIVE = "live", _("Go Live")
    DONE = "done", _("Mark As Done")


CAMPAIGN_IN_PROGRESS_STATUSES = (
    CampaignStatus.CREATED,
    CampaignStatus.RENEWAL,
    CampaignStatus.LIVE,
)


class UserCampaignRole(TextChoices):
    """Possible User Campaign Roles."""

    CHAMBER_CHAIR = "chamber_chair", _("Chamber Chair")
    VICE_CHAIR = "vice_chair", _("Vice Chair")
    TEAM_CAPTAIN = "team_captain", _("Team Captain")
    VOLUNTEER = "volunteer", _("Volunteer")
    CHAMBER_ADMIN = "chamber_admin", _("Chamber Admin")     # consider removal


class ContactMethod(TextChoices):
    """Possible Contact Methods."""

    OFFICE_CALL = "office_call", _("Office Call")
    MOBILE_CALL = "mobile_call", _("Mobile Call")
    EMAIL = "email", _("Email")
    TEXT = "text", _("Text")


class NoteType(TextChoices):
    """Note and letter types."""

    CONTRACT_NOTE = "contract_note", _("Contract Note")
    INVOICE_NOTE = "invoice_note", _("Invoice Note")
    THANKYOU_LETTER = "thankyou_letter", _("Thank You Letter")
    PE_THANKYOU_LETTER = "pe_thankyou_letter", _("Post Event Thank You Letter")
    COMPANY_THANKYOU_LETTER = (
        "company_thankyou_letter",
        _("Company Thank You Letter"),
    )
    REWARD_EMAIL = "reward_email", _("Reward Email")
    RENEWAL_LETTER = "renewal_letter", _("Renewal Letter")
    RENEWAL_CONTRACT = "renewal_contract", _("Renewal Contract")


@dataclass
class ProductCategoryData:
    """Dataclass for product category data."""

    name: str
    image_name: str = ""
    background_color: str = ""


IMAGE_ROOT_PATH = "assets/product_category_images/"
DEFAULT_PRODUCT_CATEGORIES = [
    ProductCategoryData(
        name="Signature Events",
        image_name="Category - Signature Events.png",
    ),
    ProductCategoryData(
        name="Workforce & Talent Development",
        background_color="#282B30",
    ),
    ProductCategoryData(
        name="Education Initiatives",
        background_color="#282B30",
    ),
    ProductCategoryData(
        name="Business Advocacy",
        image_name="Category - Business Advocacy.png",
    ),
    ProductCategoryData(
        name="Military Programs",
        image_name="Category - Military Affairs.png",
    ),
    ProductCategoryData(
        name="Leadership Development",
        background_color="#282B30",
    ),
    ProductCategoryData(
        name="Business Development",
        background_color="#282B30",
    ),
    ProductCategoryData(
        name="Young Professionals",
        image_name="Category - Young Professionals.png",
    ),
    ProductCategoryData(
        name="Social Media Campaigns",
        image_name="Category - Social Media Campaigns.png",
    ),
    ProductCategoryData(
        name="Marketing & Communications",
        background_color="#282B30",
    ),
    ProductCategoryData(
        name="Networking",
        background_color="#282B30",
    ),
    ProductCategoryData(
        name="Member Services",
        image_name="Category - Member Services.png",
    ),
    ProductCategoryData(
        name="Chamber Items",
        image_name="Category - Chamber Items.png",
    ),
    ProductCategoryData(
        name="Membership",
        background_color="#282B30",
    ),
]

ORDERED_ROLES = (
    UserCampaignRole.VOLUNTEER,
    UserCampaignRole.TEAM_CAPTAIN,
    UserCampaignRole.VICE_CHAIR,
    UserCampaignRole.CHAMBER_CHAIR,
    UserCampaignRole.CHAMBER_ADMIN,
)
