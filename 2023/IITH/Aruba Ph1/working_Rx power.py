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

# Debug: Print the inventory to ensure devices are loaded
logger.info(f"Inventory: {nr.inventory.hosts}")

# Define the task to run the show interfaces transceiver detail command
def run_show_transceiver_detail(task):
    command_executed = False
    authentication_failed = False
    try:
        # Connect to the device
        net_connect = task.host.get_connection("netmiko", task.nornir.config)

        # Run the show interfaces transceiver detail command
        command = "show interfaces transceiver detail"
        result = net_connect.send_command(command)
        logger.info(f"Command '{command}' executed successfully on {task.host.name}")
        command_executed = True

        # Extract required information using regular expressions
        transceiver_details = re.findall(
            r'Transceiver in (\d+).+?Rx Power\s*:\s*([\d\.]+)mW,\s*(-?\d+\.?\d*)?dBm',
            result, re.DOTALL
        )

        for interface, rx_power_mw, rx_power_dbm in transceiver_details:
            if rx_power_dbm == "-inf":
                rx_power = "-inf"
            else:
                rx_power = rx_power_mw

            print(f"Result for {task.host.name}:")
            print(f"Interface: {interface}")
            print(f"Rx Power: {rx_power}")

            # Write the output to CSV
            write_to_csv(task.host.name, task.host.hostname, interface, rx_power)
            logger.info(f"Writing content to CSV for {task.host.name}")

    except Exception as e:
        error_message = str(e)
        if "Authentication failure" in error_message:
            logger.error(f"Authentication failed for {task.host.name}: Incorrect username or password")
            write_to_csv(task.host.name, task.host.hostname, "Authentication failed")
            authentication_failed = True
        elif "timed out" in error_message:
            logger.error(f"Connection timed out for {task.host.name}")
            write_to_csv(task.host.name, task.host.hostname, "Connection timed out")
        else:
            logger.error(f"Failed to run command on {task.host.name}: {e}")
            write_to_csv(task.host.name, task.host.hostname, "Error")

    if not command_executed and not authentication_failed:
        write_to_csv(task.host.name, task.host.hostname, "No command output detected")

    return None

def write_to_csv(hostname, ip_address, interface, rx_power):
    csv_file = 'transceiver_details.csv'
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(csv_file) == 0:
            writer.writerow(["Hostname", "IP Address", "Interface", "Rx Power"])
        writer.writerow([hostname, ip_address, interface, rx_power])

def extract_error_message(error_message):
    # Extract the relevant part of the error message
    lines = error_message.splitlines()
    return lines[0]  # Return the first line of the error message

# Debug: Run the task on all devices to ensure the script works
result = nr.run(task=run_show_transceiver_detail)

print("Task completed")

# Process the CSV file to remove redundant entries
def remove_redundant_entries(csv_file):
    if not os.path.isfile(csv_file):
        logger.error(f"CSV file '{csv_file}' not found.")
        return

    with open(csv_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Get the header row
    header = rows[0]

    # Get the index of the "Hostname" and "Status" columns
    hostname_index = header.index("Hostname")
    status_index = header.index("Interface")

    # Filter out redundant entries
    filtered_rows = []
    authentication_failed_hosts = set()

    for row in rows[1:]:
        hostname = row[hostname_index]
        status = row[status_index]
        if status == "Authentication failed":
            authentication_failed_hosts.add(hostname)
        if hostname not in authentication_failed_hosts or status != "No command output detected":
            filtered_rows.append(row)

    # Write the filtered rows back to the CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(filtered_rows)

# Remove redundant entries from the CSV file
remove_redundant_entries('transceiver_details.csv')
