"""Views for ipa."""

from nautobot.apps.views import NautobotUIViewSet

from ipa import filters, forms, models, tables
from ipa.api import serializers


class IpaExampleModelUIViewSet(NautobotUIViewSet):
    """ViewSet for IpaExampleModel views."""

    bulk_update_form_class = forms.IpaExampleModelBulkEditForm
    filterset_class = filters.IpaExampleModelFilterSet
    filterset_form_class = forms.IpaExampleModelFilterForm
    form_class = forms.IpaExampleModelForm
    lookup_field = "pk"
    queryset = models.IpaExampleModel.objects.all()
    serializer_class = serializers.IpaExampleModelSerializer
    table_class = tables.IpaExampleModelTable
