import subprocess
import time

import structlog

from pimetheus.utils.config import Settings

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class GroundControl:
    """
    Interface for system and network operations on Raspberry Pi.

    Attributes:
        settings (Settings): Application configuration.
        DELAY_SECONDS (int): Delay between network commands.
        emulation (bool): Whether to use emulated responses.
    """

    settings = Settings.load()
    DELAY_SECONDS = 5

    def __init__(self) -> None:
        """
        Initialize the GroundControl system interface.

        Sets the emulation mode based on application settings.
        """

        self.emulation = self.settings.pimetheus.emulation

    def run_subprocess(self, command: list[str]) -> str:
        """
        Execute system command and return stdout.

        Parameters:
            command (list[str]): Command with arguments.

        Returns:
            str: Command stdout output.

        Raises:
            subprocess.CalledProcessError: If command fails.
        """

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                shell=False,
            )
            logger.info("Executed command", command=command)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.exception("Failed to execute command", command=command, stdout=e.stdout, stderr=e.stderr)
            raise

    def get_gpu_temperature(self) -> str:
        """
        Get GPU temperature.

        Returns:
            str: Temperature in Celsius.

        Raises:
            subprocess.CalledProcessError: If command fails.
        """

        if self.emulation:
            temp = "42"
            logger.warning("Using EMULATION settings", temperature=temp)
            return temp
        else:
            commands = ["vcgencmd", "measure_temp"]
            result = self.run_subprocess(commands)
            temp = result.replace("temp=", "").replace("'C", "")
            logger.info("Received GPU temperature", temperature=temp)
            return temp

    def get_uptime(self) -> str:
        """
        Get system uptime.

        Returns:
            str: Human-readable uptime.

        Raises:
            subprocess.CalledProcessError: If command fails.
        """

        if self.emulation:
            uptime = "1 weeks, 1 days, 1 hours, 1 minutes"
            logger.warning("Using EMULATION settings", uptime=uptime)
            return uptime
        else:
            commands = ["uptime", "-p"]
            result = self.run_subprocess(commands)
            uptime = result.removeprefix("up ").strip()
            logger.info("Received uptime", uptime=uptime)
            return uptime

    def renew_dhclient(self) -> None:
        """
        Renew DHCP lease.

        Raises:
            subprocess.CalledProcessError: If command fails.
        """

        if self.emulation:
            logger.warning("Using EMULATION settings", renew_dhclient=True)
        else:
            time.sleep(self.DELAY_SECONDS)

            commands = ["sudo", "dhclient", "-r"]
            self.run_subprocess(commands)
            logger.info("Released DHCLIENT")

            time.sleep(self.DELAY_SECONDS)

            commands = ["sudo", "dhclient"]
            self.run_subprocess(commands)
            logger.info("Renewed DHCLIENT")

            time.sleep(self.DELAY_SECONDS)
