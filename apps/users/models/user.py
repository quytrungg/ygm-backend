from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import citext
from imagekit import models as imagekitmodels
from imagekit.processors import ResizeToFill, Transpose
from safedelete.managers import SafeDeleteManager

from apps.core.constants import MAX_PHONE_NUMBER_LENGTH, MAX_ZIP_CODE_LENGTH
from apps.core.models import BaseModel
from apps.users.constants import UserRole


class UserManager(SafeDeleteManager, DjangoUserManager):
    """Adjusted user manager that works w/o `username` field."""

    # pylint: disable=arguments-differ
    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # pylint: disable=arguments-differ
    def create_superuser(self, email, password=None, **extra_fields):
        """Create superuser instance (used by `createsuperuser` cmd)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(
    BaseModel,
    AbstractBaseUser,
    PermissionsMixin,
):
    """Custom user model without username."""

    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=30,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=30,
        blank=True,
    )
    email = citext.CIEmailField(
        verbose_name=_("Email address"),
        max_length=254,  # to be compliant with RFCs 3696 and 5321
    )
    is_staff = models.BooleanField(
        verbose_name=_("Staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site.",
        ),
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active.",
        ),
    )
    mobile_phone = models.CharField(
        verbose_name=_("Mobile phone"),
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
    )
    work_phone = models.CharField(
        verbose_name=_("Work phone"),
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
    )
    home_phone = models.CharField(
        verbose_name=_("Home phone"),
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
    )
    fax = models.CharField(
        verbose_name=_("Fax"),
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
    )
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
        blank=True,
    )
    address = models.CharField(
        verbose_name=_("Address"),
        max_length=255,
        blank=True,
    )
    avatar = imagekitmodels.ProcessedImageField(
        verbose_name=_("Avatar"),
        blank=True,
        null=True,
        upload_to=settings.DEFAULT_MEDIA_PATH,
        max_length=512,
        processors=[Transpose()],
        options={
            "quality": 100,
        },
    )
    avatar_thumbnail = imagekitmodels.ImageSpecField(
        source="avatar",
        processors=[
            ResizeToFill(50, 50),
        ],
    )
    birthday = models.DateField(
        verbose_name=_("Birthday"),
        null=True,
    )
    home_address = models.CharField(
        verbose_name=_("Home address"),
        max_length=255,
        blank=True,
    )
    home_city = models.CharField(
        verbose_name=_("Home city"),
        max_length=255,
        blank=True,
    )
    home_state = models.CharField(
        verbose_name=_("Home state"),
        max_length=2,
        blank=True,
    )
    home_zip_code = models.CharField(
        verbose_name=_("Home zip code"),
        max_length=MAX_ZIP_CODE_LENGTH,
        blank=True,
    )
    role = models.CharField(
        max_length=255,
        choices=UserRole.choices,
        verbose_name=_("Role"),
        default=UserRole.VOLUNTEER,
    )
    company = models.CharField(
        max_length=255,
        verbose_name=_("Company"),
        blank=True,
    )
    chamber = models.ForeignKey(
        to="chambers.Chamber",
        related_name="users",
        null=True,
        blank=True,
        verbose_name=_("Chamber"),
        on_delete=models.CASCADE,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )
    external_chamber_id = models.IntegerField(
        verbose_name=_("chamber ID in old DB"),
        blank=True,
        null=True,
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    ROLES = UserRole

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        constraints = [
            models.UniqueConstraint(
                fields=("email",),
                name="unique_user_email",
                condition=models.Q(deleted_at__isnull=True),
            ),
        ]

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return self.email

    def clean_birthday(self):
        """Ensure that birthday is not in the future."""
        if self.birthday and self.birthday > timezone.now().date():
            raise ValidationError(
                _("Birthday cannot be in the future."),
            )

    @property
    def campaign_role(self):
        """Return campaign role for user."""
        if self.role in (UserRole.SUPER_ADMIN, UserRole.CHAMBER_ADMIN):
            return self.role
        # pylint: disable=no-member
        campaign = self.chamber.campaigns.last()
        user_campaign = self.user_campaigns.filter(
            campaign=campaign,
        ).first()
        return user_campaign.role if user_campaign else self.role

    @property
    def full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
