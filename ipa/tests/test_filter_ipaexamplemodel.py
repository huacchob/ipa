"""Test IpaExampleModel Filter."""

from django.test import TestCase

from ipa import filters, models
from ipa.tests import fixtures


class IpaExampleModelFilterTestCase(TestCase):
    """IpaExampleModel Filter Test Case."""

    queryset = models.IpaExampleModel.objects.all()
    filterset = filters.IpaExampleModelFilterSet

    @classmethod
    def setUpTestData(cls):
        """Setup test data for IpaExampleModel Model."""
        fixtures.create_ipaexamplemodel()

    def test_q_search_name(self):
        """Test using Q search with name of IpaExampleModel."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for IpaExampleModel."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
