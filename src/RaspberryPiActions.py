import os
import time
from Blackbox import Blackbox

blackbox = Blackbox("RPiAction")
blackbox_logger = blackbox.logger


def get_raspi_gpu_temperature():
    try:
        blackbox_logger.info("Initialized method get_raspi_gpu_temperature")
        cmd = "vcgencmd measure_temp"
        line = os.popen(cmd).readline().strip()
        temp = line.split("=")[1].split("'")[0]
        blackbox_logger.info(f"RETURN raspi temperature: {temp}")
        return temp
    except Exception as e:
        blackbox_logger.warning("method get_raspi_gpu_temperature")
        blackbox_logger.exception(f"RETURN: {e}")


def get_raspi_up_time():
    try:
        blackbox_logger.info("Initialized method get_raspi_uptime")
        cmd = "uptime -p"
        up_time = os.popen(cmd).readline().strip()
        up_time_str = up_time[3::]
        blackbox_logger.info(f"RETURN raspi up time: {up_time_str}")
        return up_time_str
    except Exception as e:
        blackbox_logger.warning("method get_raspi_uptime")
        blackbox_logger.exception(f"RETURN: {e}")


def renew_raspi_dhclient():
    try:
        blackbox_logger.info("Initialized method renew_raspi_dhclient")
        time.sleep(5)
        cmd = "sudo dhclient -r"
        stream = os.popen(cmd)
        output = stream.read()
        blackbox_logger.info(f"RETURN release info {output}")
        time.sleep(5)
        cmd = "sudo dhclient"
        stream = os.popen(cmd)
        output = stream.readline()
        blackbox_logger.info(f"RETURN renewal info {output}")
        time.sleep(5)
    except Exception as e:
        blackbox_logger.warning("method renew_raspi_dhclient")
        blackbox_logger.exception(f"RETURN: {e}")
