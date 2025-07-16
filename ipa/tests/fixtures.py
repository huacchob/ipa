"""Create fixtures for tests."""

from ipa.models import IpaExampleModel


def create_ipaexamplemodel():
    """Fixture to create necessary number of IpaExampleModel for tests."""
    IpaExampleModel.objects.create(name="Test One")
    IpaExampleModel.objects.create(name="Test Two")
    IpaExampleModel.objects.create(name="Test Three")
