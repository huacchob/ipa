"""API views for ipa."""

from nautobot.apps.api import NautobotModelViewSet

from ipa import filters, models
from ipa.api import serializers


class IpaExampleModelViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """IpaExampleModel viewset."""

    queryset = models.IpaExampleModel.objects.all()
    serializer_class = serializers.IpaExampleModelSerializer
    filterset_class = filters.IpaExampleModelFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
