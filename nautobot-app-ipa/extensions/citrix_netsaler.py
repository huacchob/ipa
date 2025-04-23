"""default network_importer API-based driver for Citrix Netscaler."""

import json
import ssl
from os import path
from typing import TYPE_CHECKING

from nornir.core.exceptions import NornirSubTaskError
from nornir.core.task import MultiResult, Result, Task
from nornir_nautobot.exceptions import NornirNautobotException
from nornir_nautobot.plugins.tasks.dispatcher.mikrotik_routeros import (
    NetmikoMikrotikRouteros as DefaultNautobotNornirDriver,
)
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

try:
    import routeros_api  # pylint: disable=E0401
except ImportError:
    routeros_api = None
from nornir_nautobot.utils.helpers import get_error_message

if TYPE_CHECKING:
    from logging import Logger

    from nautobot.dcim.models import Device

    if routeros_api:
        from routeros_api import RouterOsApiPool
        from routeros_api.api import RouterOsApi
        from routeros_api.resource import RouterOsResource

NETMIKO_DEVICE_TYPE = "netscaler"


class ModifiedMikrotikDriver(DefaultNautobotNornirDriver):
    """Simply override the config_command class attribute in the subclass."""

    config_command: str = "export terse verbose hide-sensitive"
    # tcp_port: int = 8729

    api_config_command: list[str] = [
        "/system/identity",
        "/user",
        "/interface",
        "/ip/address",
        "/system/ntp/client",
        "/ip/dns",
        "/snmp/community",
        "/system/logging/action",
    ]

    @classmethod
    def get_config(  # pylint: disable=R0913,R0914
        cls,
        task: Task,
        logger: Logger,
        obj: Device,
        backup_file: str,
        remove_lines: list[str],
        substitute_lines: list[str],
    ) -> Result | None:
        """
        Retrieve and process the configuration from a network device via CLI and API.

        This method performs the following:
          - Sets up the task's device platform for CLI backup.
          - Executes a CLI command using Netmiko (with timing enabled) to obtain the device's running configuration.
          - Processes the CLI backup by removing and substituting specified lines and saves the result to a backup file.
          - Validates and utilizes the RouterOS API to retrieve configuration data if the dependency is available.
          - Processes the API configuration similarly to the CLI configuration.
          - Returns a Result object containing the processed API configuration.

        Args:
          cls:
              The context being passed in.
          task (Task):
              The task instance representing the network device operation.
          logger:
              The logger object used for recording debug and error messages.
          obj:
              (Device): A Nautobot Device Django ORM object instance.
          backup_file (str):
              The file path where the backup configuration will be stored.
          remove_lines (list[str]):
              A list of string patterns or specific lines to remove from the configuration output.
          substitute_lines (list[str]):
              A list of string patterns or mappings to substitute within the configuration output.

        Returns:
          Result:
              A result object containing the processed API configuration. The object includes the host details
              and a dictionary with the key "config" mapping to the processed configuration string.

        Raises:
          NornirNautobotException:
              If the CLI command execution fails, if the RouterOS API dependency is unavailable,
              or if any error occurs during API configuration retrieval or processing.

        Notes:
          - The function assumes that `cls.config_command` and `cls.api_config_command` are defined.
          - The CLI configuration is handled with a delay factor to ensure complete retrieval.
          - The SSL context is created and configured to support plaintext login using specific cipher settings.
          - The method processes the configuration data by invoking `cls._process_config`, applying removals
            and substitutions as specified.
        """
        task.host.platform = NETMIKO_DEVICE_TYPE
        # CLI CONFIGURATION
        try:
            # we need to override this portion and set use_timing to True, otherwise we don't get the full cli backup
            result: MultiResult = task.run(
                task=netmiko_send_command,
                use_timing=True,
                command_string=cls.config_command,
                delay_factor=10,
            )
        except NornirSubTaskError as exc:
            exc_result: Result = exc.result
            error_msg: str = f"Failed with an unknown issue. `{exc_result.exception}`"
            logger.error(msg=error_msg, extra={"object": obj})
            raise NornirNautobotException(error_msg)

        if result[0].failed:
            return result
        base_name, ext = path.splitext(p=backup_file)
        logger.debug(msg=base_name)
        cli_backup_file: str = f"{base_name}-cli{ext}"
        logger.debug(msg=f"CLI backup file will be: {cli_backup_file}")

        # Running configuration
        _running_config: str = result[0].result
        # This seems to be where it processes and saves to a backup file
        cls._process_config(
            logger=logger,
            running_config=_running_config,
            remove_lines=remove_lines,
            substitute_lines=substitute_lines,
            backup_file=cli_backup_file,
        )
        # API CONFIGURATION
        logger.debug(
            msg=f"Executing API get_config for {task.host.name} on {task.host.platform}",
        )
        if not routeros_api:
            error_msg = get_error_message(
                error_code="E1020",
                dependency="routeros_api",
            )
            logger.error(msg=error_msg, extra={"object": obj})
            raise NornirNautobotException(error_msg)

        sslctx: ssl.SSLContext = ssl.create_default_context()
        sslctx.set_ciphers(
            "ADH-AES256-GCM-SHA384:ADH-AES256-SHA256:@SECLEVEL=0",
        )

        # Mikrotik API connection
        connection: RouterOsApiPool = RouterOsApiPool(
            host=task.host.hostname,
            username=task.host.username,
            password=task.host.password,
            use_ssl=True,
            ssl_context=sslctx,
            plaintext_login=True,
        )
        config_data: dict[str, str] | dict[None, None] = {}
        try:
            # Authenticate to the API
            api: RouterOsApi = connection.get_api()
        except Exception as error:
            error_msg = get_error_message(error_code="E1021", error=error)
            logger.error(msg=error_msg, extra={"object": obj})
            raise NornirNautobotException(error_msg)
        for endpoint in cls.api_config_command:
            try:
                resource: RouterOsResource = api.get_resource(path=endpoint)

                # Assign config value to endpoint
                config_data[endpoint] = resource.get()
            except Exception as error:
                error_msg = get_error_message(error_code="E1022", error=error)
                logger.error(msg=error_msg, extra={"object": obj})
                raise NornirNautobotException(error_msg)

        connection.disconnect()
        if config_data:
            api_running_config: str = json.dumps(obj=config_data, indent=4)

            # Process and save the API configuration
            api_processed_config: str = cls._process_config(
                logger=logger,
                running_config=api_running_config,
                remove_lines=remove_lines,
                substitute_lines=substitute_lines,
                backup_file=backup_file,
            )
            return Result(
                host=task.host,
                result={"config": api_processed_config},
            )
        return None

    @staticmethod
    def merge_config(
        task: Task,
        logger: Logger,
        obj: Device,
        config: str,
    ) -> Result:
        """Send configuration to merge on the device.

        Args:
            task (Task): Nornir Task.
            logger (NornirLogger): Custom NornirLogger object to reflect job_results (via Nautobot Jobs) and Python logger.
            obj (Device): A Nautobot Device Django ORM object instance.
            config (str): The config set.

        Raises:
            NornirNautobotException: Authentication error.
            NornirNautobotException: Timeout error.
            NornirNautobotException: Other exception.

        Returns:
            Result: Nornir Result object with a dict as a result containing what changed and the result of the push.
        """
        # Adjust platform type to switch to CLI config push
        NETMIKO_FAIL_MSG: list[str] = ["bad", "failed", "failure"]  # pylint: disable=C0103
        task.host.platform = NETMIKO_DEVICE_TYPE
        logger.info(msg="Config merge starting", extra={"object": obj})

        try:
            # Push API configuration
            config_list: list[str] = config.splitlines()
            push_result_api: MultiResult = task.run(
                task=netmiko_send_config,
                config_commands=config_list,
            )

            # Check if there's any CLI configuration to push
            cli_configuration: str = obj.cf.get("cli_configuration", "")
            if cli_configuration:
                cli_config_list: list[str] = cli_configuration.splitlines()

                # Send command
                push_result_cli: MultiResult = task.run(
                    task=netmiko_send_config,
                    config_commands=cli_config_list,
                )
                push_results: list[Result] = [push_result_api[0], push_result_cli[0]]
            else:
                push_results: list[Result] = [push_result_api[0]]

        except NornirSubTaskError as exc:
            exc_result: Result = exc.result
            logger.error(
                msg=f"Failed with error: `{exc_result.exception}`",
                extra={"object": obj},
            )
            raise NornirNautobotException()

        failed: bool = any(any(msg in result.result.lower() for msg in NETMIKO_FAIL_MSG) for result in push_results)
        if failed:
            logger.warning(
                msg="Config merged with errors, please check full info log below.",
                extra={"object": obj},
            )
            for result in push_results:
                logger.error(
                    msg=f"result: {result.result}",
                    extra={"object": obj},
                )
                result.failed = True
        else:
            logger.info(
                msg="Config merged successfully.",
                extra={"object": obj},
            )
            for result in push_results:
                logger.info(
                    msg=f"result: {result.result}",
                    extra={"object": obj},
                )
                result.failed = False

        changed: bool = any(result.changed for result in push_results)

        return Result(
            host=task.host,
            result={
                "changed": changed,
                "result": "\n".join(result.result for result in push_results),
                "failed": failed,
            },
        )
