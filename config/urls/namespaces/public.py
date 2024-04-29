from apps.campaigns.api.public.urls import urlpatterns as campaign_urls
from apps.members.api.public.urls import urlpatterns as member_urls

app_name = "public"

urlpatterns = campaign_urls + member_urls
