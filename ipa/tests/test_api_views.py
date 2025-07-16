"""Unit tests for ipa."""

from nautobot.apps.testing import APIViewTestCases

from ipa import models
from ipa.tests import fixtures


class IpaExampleModelAPIViewTest(APIViewTestCases.APIViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the API viewsets for IpaExampleModel."""

    model = models.IpaExampleModel
    create_data = [
        {
            "name": "Test Model 1",
            "description": "test description",
        },
        {
            "name": "Test Model 2",
        },
    ]
    bulk_update_data = {"description": "Test Bulk Update"}

    @classmethod
    def setUpTestData(cls):
        fixtures.create_ipaexamplemodel()
