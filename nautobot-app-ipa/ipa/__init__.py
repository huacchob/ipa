"""App declaration for ipa."""

# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class IpaConfig(NautobotAppConfig):
    """App configuration for the ipa app."""

    name = "ipa"
    verbose_name = "Ipa"
    version = __version__
    author = "Network to Code, LLC"
    description = "Ipa."
    base_url = "ipa"
    required_settings = []
    min_version = "2.4.7"
    max_version = "2.9999.9999"
    default_settings = {}
    caching_config = {}
    docs_view_name = "plugins:ipa:docs"


config = IpaConfig  # pylint:disable=invalid-name
