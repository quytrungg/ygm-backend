from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class ChamberBranding(BaseModel):
    """Represent a chamber's branding setting.

    Attributes:
        - site_primary_color: Default site primary color
        - site_secondary_color: Default site secondary color
        - site_alternate_color: Default site alternate color
        - chamber_logo: Chamber's logo
        - trc_logo: TRC's logo
        - landing_bg: Landing background image
        - headline: Headline
        - public_prelaunch_msg: Message displayed in public site
        - volunteer_prelaunch_msg: Message displayed in volunteer site

    """

    chamber = models.OneToOneField(
        to="chambers.Chamber",
        on_delete=models.CASCADE,
        verbose_name=_("Chamber"),
        related_name="branding",
    )
    site_primary_color = models.CharField(
        verbose_name=_("Site's default primary color"),
        max_length=7,
    )
    site_secondary_color = models.CharField(
        verbose_name=_("Site's default secondary color"),
        max_length=7,
    )
    site_alternate_color = models.CharField(
        verbose_name=_("Site's default alternate color"),
        max_length=7,
    )
    chamber_logo = models.FileField(  # noqa: DJ01
        verbose_name=_("Chamber Logo"),
        max_length=512,
        null=True,
        blank=True,
    )
    trc_logo = models.FileField(  # noqa: DJ01
        verbose_name=_("Chamber Logo"),
        max_length=512,
        null=True,
        blank=True,
    )
    landing_bg = models.FileField(  # noqa: DJ01
        verbose_name=_("Landing background image"),
        max_length=512,
        null=True,
        blank=True,
    )
    headline = models.CharField(
        verbose_name=_("Headline"),
        max_length=50,
    )
    public_prelaunch_msg = models.TextField(
        verbose_name=_("Public pre-launch message"),
    )
    volunteer_prelaunch_msg = models.TextField(
        verbose_name=_("Volunteer pre-launch message"),
    )

    class Meta:
        verbose_name = _("Branding")
        verbose_name_plural = _("Brandings")

    def __str__(self):
        return self.chamber.name
