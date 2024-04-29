from apps.members import autocomplete as members_autocomplete
from apps.incentives import autocomplete as incentives_autocomplete
from apps.users import autocomplete as users_autocomplete
from apps.chambers import autocomplete as chambers_autocomplete
from apps.campaigns import autocomplete as campaigns_autocomplete
from apps.timelines import autocomplete as timelines_autocomplete
from apps.resources import autocomplete as resources_autocomplete
from django.urls import path

urlpatterns = [
    path(
        "timeline-category-autocomplete/",
        timelines_autocomplete.TimelineCategoryAutocompleteView.as_view(),
        name="timeline-category-autocomplete",
    ),
    path(
        "resource-category-autocomplete/",
        resources_autocomplete.ResourceCategoryAutocompleteView.as_view(),
        name="resource-category-autocomplete",
    ),
    path(
        "member-autocomplete/",
        members_autocomplete.MemberAutocompleteView.as_view(),
        name="member-autocomplete",
    ),
    path(
        "contract-autocomplete/",
        members_autocomplete.ContractAutocompleteView.as_view(),
        name="contract-autocomplete",
    ),
    path(
        "incentive-autocomplete/",
        incentives_autocomplete.IncentiveAutocompleteView.as_view(),
        name="incentive-autocomplete",
    ),
    path(
        "user-autocomplete/",
        users_autocomplete.UserAutocompleteView.as_view(),
        name="user-autocomplete",
    ),
    path(
        "chamber-autocomplete/",
        chambers_autocomplete.ChamberAutocompleteView.as_view(),
        name="chamber-autocomplete",
    ),
    path(
        "stored-member-autocomplete/",
        chambers_autocomplete.StoredMemberAutocompleteView.as_view(),
        name="stored-member-autocomplete",
    ),

    path(
        "campaign-autocomplete/",
        campaigns_autocomplete.CampaignAutocompleteView.as_view(),
        name="campaign-autocomplete",
    ),
    path(
        "product-category-autocomplete/",
        campaigns_autocomplete.ProductCategoryAutocompleteView.as_view(),
        name="product-category-autocomplete",
    ),
    path(
        "product-autocomplete/",
        campaigns_autocomplete.ProductAutocompleteView.as_view(),
        name="product-autocomplete",
    ),
    path(
        "level-autocomplete/",
        campaigns_autocomplete.LevelAutocompleteView.as_view(),
        name="level-autocomplete",
    ),
    path(
        "team-autocomplete/",
        campaigns_autocomplete.TeamAutocompleteView.as_view(),
        name="team-autocomplete",
    ),
    path(
        "user-campaign-autocomplete/",
        campaigns_autocomplete.UserCampaignAutocompleteView.as_view(),
        name="user-campaign-autocomplete",
    ),
]
