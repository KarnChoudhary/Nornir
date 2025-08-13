from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging
import csv
import re
import os

# Configure logging
logging.basicConfig(filename='switch_identification.log', level=logging.DEBUG)
logger = logging.getLogger("nornir")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the task to identify the switch type
def identify_switch_type(task):
    try:
        # Connect to the device
        net_connect = task.host.get_connection("netmiko", task.nornir.config)

        # Increase read timeout
        net_connect.timeout = 30

        # Try HPE command
        command = "screen-length disable"
        result = net_connect.send_command(command, expect_string=r'[\#\>\]]')
        command = "display version"
        result = net_connect.send_command(command, expect_string=r'[\#\>\]]')
        if "HP" in result or "Comware" in result:
            logger.info(f"{task.host.name} is an HPE switch")
            write_to_csv(task.host.name, task.host.hostname, "HPE")
            return

        # Try Cisco command
        command = "show version"
        result = net_connect.send_command(command, expect_string=r'[\#\>\]]')
        if "Cisco" in result:
            logger.info(f"{task.host.name} is a Cisco switch")
            write_to_csv(task.host.name, task.host.hostname, "Cisco")
            return

        # If none of the above, log as unknown
        logger.info(f"{task.host.name} is an unknown switch type")
        write_to_csv(task.host.name, task.host.hostname, "Unknown")

    except Exception as e:
        logger.error(f"Failed to identify switch type for {task.host.name}: {e}")
        write_to_csv(task.host.name, task.host.hostname, "Error")

def write_to_csv(hostname, ip_address, switch_type, error_message=""):
    csv_file = 'switch_identification.csv'
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(csv_file) == 0:
            writer.writerow(["Hostname", "IP Address", "Switch Type", "Error Message"])
        writer.writerow([hostname, ip_address, switch_type, error_message])

# Filter the devices and run the task
result = nr.run(task=identify_switch_type)

print("Task completed")
