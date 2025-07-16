"""Filtering for ipa."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from ipa import models


class IpaExampleModelFilterSet(NautobotFilterSet, NameSearchFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for IpaExampleModel."""

    class Meta:
        """Meta attributes for filter."""

        model = models.IpaExampleModel

        # add any fields from the model that you would like to filter your searches by using those
        fields = ["id", "name", "description"]
