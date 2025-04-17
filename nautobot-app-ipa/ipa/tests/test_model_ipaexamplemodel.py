"""Test IpaExampleModel."""

from django.test import TestCase

from ipa import models


class TestIpaExampleModel(TestCase):
    """Test IpaExampleModel."""

    def test_create_ipaexamplemodel_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        ipaexamplemodel = models.IpaExampleModel.objects.create(name="Development")
        self.assertEqual(ipaexamplemodel.name, "Development")
        self.assertEqual(ipaexamplemodel.description, "")
        self.assertEqual(str(ipaexamplemodel), "Development")

    def test_create_ipaexamplemodel_all_fields_success(self):
        """Create IpaExampleModel with all fields."""
        ipaexamplemodel = models.IpaExampleModel.objects.create(name="Development", description="Development Test")
        self.assertEqual(ipaexamplemodel.name, "Development")
        self.assertEqual(ipaexamplemodel.description, "Development Test")
