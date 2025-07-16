"""Forms for ipa."""

from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from ipa import models


class IpaExampleModelForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """IpaExampleModel creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.IpaExampleModel
        fields = [
            "name",
            "description",
        ]


class IpaExampleModelBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """IpaExampleModel bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.IpaExampleModel.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class IpaExampleModelFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.IpaExampleModel
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Slug.",
    )
    name = forms.CharField(required=False, label="Name")
