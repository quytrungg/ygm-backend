from drf_spectacular.utils import extend_schema, extend_schema_view

from .chamber_admin import views

extend_schema_view(
    decline=extend_schema(request=None),
)(views.ContractViewSet)
