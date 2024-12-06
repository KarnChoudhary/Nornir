from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging
import csv
import re
import os

# Configure logging
logging.basicConfig(
    filename='nornir.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("nornir")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the task to identify the device type
def identify_device_type(task):
    try:
        # Connect to the device
        net_connect = task.host.get_connection("netmiko", task.nornir.config)

        # Run a command to identify the device type
        command = "show version"
        result = net_connect.send_command(command)
        logger.info(f"Command '{command}' executed successfully on {task.host.name}")

        # Identify the device type based on the output
        if "HPE" in result or "Comware" in result:
            device_type = "HPE"
        elif "Aruba" in result:
            device_type = "Aruba"
        else:
            device_type = "Unknown"

        print(f"Device Type for {task.host.name}: {device_type}")

        # Write the output to CSV
        write_to_csv(task.host.name, task.host.hostname, device_type)
        logger.info(f"Writing content to CSV for {task.host.name}")

    except Exception as e:
        error_message = str(e)
        if "Authentication failure" in error_message:
            logger.error(f"Authentication failed for {task.host.name}: Incorrect username or password")
            write_to_csv(task.host.name, task.host.hostname, "Authentication failed")
        elif "timed out" in error_message:
            logger.error(f"Connection timed out for {task.host.name}")
            write_to_csv(task.host.name, task.host.hostname, "Connection timed out")
        else:
            logger.error(f"Failed to identify device type on {task.host.name}: {e}")
            write_to_csv(task.host.name, task.host.hostname, "Error")

    return None

def write_to_csv(hostname, ip_address, device_type):
    csv_file = 'device_type_identification.csv'
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(csv_file) == 0:
            writer.writerow(["Hostname", "IP Address", "Device Type"])
        writer.writerow([hostname, ip_address, device_type])

# Filter the devices and run the task
result = nr.run(task=identify_device_type)

print("Task completed")
