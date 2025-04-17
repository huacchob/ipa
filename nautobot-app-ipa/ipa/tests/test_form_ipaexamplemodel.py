"""Test ipaexamplemodel forms."""

from django.test import TestCase

from ipa import forms


class IpaExampleModelTest(TestCase):
    """Test IpaExampleModel forms."""

    def test_specifying_all_fields_success(self):
        form = forms.IpaExampleModelForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.IpaExampleModelForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_ipaexamplemodel_is_required(self):
        form = forms.IpaExampleModelForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
