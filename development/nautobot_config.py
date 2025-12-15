"""Nautobot development configuration file."""

import logging
import logging.handlers
import os
import sys

from celery import signals
from nautobot.core.settings import *  # noqa: F403  # pylint: disable=wildcard-import,unused-wildcard-import
from nautobot.core.settings_funcs import is_truthy

LOG_PATH = "/var/log/jobs_logs.log"


def _make_file_handler() -> logging.Handler:
    """Create a rotating file handler with a formatter that will include tracebacks."""
    h = logging.handlers.RotatingFileHandler(
        filename=LOG_PATH,
        maxBytes=15 * 1024 * 1024,  # 15 MB
        backupCount=5,
        encoding="utf-8",
    )
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"))
    return h


@signals.after_setup_logger.connect
def setup_celery_root_logging(logger: logging.Logger, **kwargs):
    """
    Add file handler to Celery's *global* logger so worker/internal errors
    (including tracebacks) are captured.
    """
    logger.addHandler(_make_file_handler())


@signals.after_setup_task_logger.connect
def setup_celery_task_logging(logger: logging.Logger, **kwargs):
    """
    Add file handler to task loggers (get_task_logger) so your task code logs
    end up in the same file.
    """
    logger.addHandler(_make_file_handler())


@signals.task_failure.connect
def log_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, einfo=None, **kw):
    """
    Ensure tracebacks are written even if other logging config gets in the way.
    Celery passes `einfo` (ExceptionInfo) which contains the traceback.
    """
    log = logging.getLogger("celery.app.trace")
    # Use the provided exception info so the full traceback is emitted.
    exc_info = getattr(einfo, "exc_info", True)
    log.error(
        "Task failed: %s (task=%s id=%s args=%r kwargs=%r)",
        exception,
        getattr(sender, "name", sender),
        task_id,
        args,
        kwargs,
        exc_info=exc_info,
    )


#
# Debug
#

DEBUG = is_truthy(os.getenv("NAUTOBOT_DEBUG", "false"))
_TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

if DEBUG and not _TESTING:
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: True}

    if "debug_toolbar" not in INSTALLED_APPS:  # noqa: F405
        INSTALLED_APPS.append("debug_toolbar")  # noqa: F405
    if "debug_toolbar.middleware.DebugToolbarMiddleware" not in MIDDLEWARE:  # noqa: F405
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

#
# Misc. settings
#

ALLOWED_HOSTS = os.getenv("NAUTOBOT_ALLOWED_HOSTS", "").split(" ")
SECRET_KEY = os.getenv("NAUTOBOT_SECRET_KEY", "")

#
# Database
#

nautobot_db_engine = os.getenv("NAUTOBOT_DB_ENGINE", "django.db.backends.postgresql")
default_db_settings = {
    "django.db.backends.postgresql": {
        "NAUTOBOT_DB_PORT": "5432",
    },
    "django.db.backends.mysql": {
        "NAUTOBOT_DB_PORT": "3306",
    },
}
DATABASES = {
    "default": {
        "NAME": os.getenv("NAUTOBOT_DB_NAME", "nautobot"),  # Database name
        "USER": os.getenv("NAUTOBOT_DB_USER", ""),  # Database username
        "PASSWORD": os.getenv("NAUTOBOT_DB_PASSWORD", ""),  # Database password
        "HOST": os.getenv("NAUTOBOT_DB_HOST", "localhost"),  # Database server
        "PORT": os.getenv(
            "NAUTOBOT_DB_PORT", default_db_settings[nautobot_db_engine]["NAUTOBOT_DB_PORT"]
        ),  # Database port, default to postgres
        "CONN_MAX_AGE": int(os.getenv("NAUTOBOT_DB_TIMEOUT", "300")),  # Database timeout
        "ENGINE": nautobot_db_engine,
    }
}

# Ensure proper Unicode handling for MySQL
if DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
    DATABASES["default"]["OPTIONS"] = {"charset": "utf8mb4"}

#
# Redis
#

# The django-redis cache is used to establish concurrent locks using Redis.
# Inherited from nautobot.core.settings
# CACHES = {....}

#
# Celery settings are not defined here because they can be overloaded with
# environment variables. By default they use `CACHES["default"]["LOCATION"]`.
#

#
# Logging
#

LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

# Verbose logging during normal development operation, but quiet logging during unit test execution
if not _TESTING:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "normal": {
                "format": "%(asctime)s.%(msecs)03d %(levelname)-7s %(name)s : %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "verbose": {
                "format": "%(asctime)s.%(msecs)03d %(levelname)-7s %(name)-20s %(filename)-15s %(funcName)30s() : %(message)s",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "normal_console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "normal",
            },
            "verbose_console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "django": {"handlers": ["normal_console"], "level": "INFO"},
            "nautobot": {
                "handlers": ["verbose_console" if DEBUG else "normal_console"],
                "level": LOG_LEVEL,
            },
        },
    }

#
# Apps
#

# Enable installed Apps. Add the name of each App to the list.
PLUGINS = [
    "ipa",
    "nautobot_plugin_nornir",
    "nautobot_golden_config",
    "netscaler_ext",
]

# Apps configuration settings. These settings are used by various Apps that the user may have installed.
# Each key in the dictionary is the name of an installed App and its value is a dictionary of settings.
PLUGINS_CONFIG = {
    "nautobot_plugin_nornir": {
        "nornir_settings": {
            "credentials": "nautobot_plugin_nornir.plugins.credentials.nautobot_secrets.CredentialsNautobotSecrets",
            "runner": {
                "plugin": "threaded",
                "options": {
                    "num_workers": 20,
                },
            },
        },
    },
    "nautobot_golden_config": {
        "per_feature_bar_width": 0.15,
        "per_feature_width": 13,
        "per_feature_height": 4,
        "enable_backup": True,
        "enable_compliance": True,
        "enable_intended": True,
        "enable_sotagg": True,
        "enable_plan": True,
        "enable_deploy": True,
        "enable_postprocessing": True,
        "sot_agg_transposer": None,
        "postprocessing_callables": [],
        "postprocessing_subscribed": [],
        "jinja_env": {
            "undefined": "jinja2.StrictUndefined",
            "trim_blocks": True,
            "lstrip_blocks": False,
        },
        "custom_dispatcher": {
            "citrix_netscaler": "netscaler_ext.plugins.tasks.dispatcher.citrix_netscaler.NetmikoCitrixNetscaler",
            "cisco_nxos": "netscaler_ext.plugins.tasks.dispatcher.cisco_nxos.NetmikoCiscoNxos",
            "cisco_vmanage": "netscaler_ext.plugins.tasks.dispatcher.cisco_vmanage.NetmikoCiscoVmanage",
            "cisco_meraki": "netscaler_ext.plugins.tasks.dispatcher.cisco_meraki.NetmikoCiscoMeraki",
            "cisco_apic": "netscaler_ext.plugins.tasks.dispatcher.cisco_apic.NetmikoCiscoApic",
        },
        "get_custom_remediation": "netscaler_ext.plugins.tasks.remediation.custom_remediation.remediation_func",
        # "default_deploy_status": "Not Approved",
        # "get_custom_compliance": "my.custom_compliance.func"
    },
}
