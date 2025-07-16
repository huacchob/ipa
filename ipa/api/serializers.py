"""API serializers for ipa."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from ipa import models


class IpaExampleModelSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """IpaExampleModel Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.IpaExampleModel
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []
