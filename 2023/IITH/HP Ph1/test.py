from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging
import csv
import re
import os

# Configure logging
logging.basicConfig(filename='demo_nornir.log', level=logging.DEBUG)
logger = logging.getLogger("nornir")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the task to handle the password change prompt and run the display transceiver diagnos interface command
def handle_password_change_and_run_command(task):
    password_change_commands = [
        "undo password-control change-password first-login enable",
        "undo password-control length enable",
        "undo password-control complexity user-name check",
        "save"
    ]
    command_executed = False
    authentication_failed = False
    try:
        # Connect to the device
        net_connect = task.host.get_connection("netmiko", task.nornir.config)

        # Handle the password change prompt
        output = net_connect.send_command_timing("", strip_prompt=False, strip_command=False)
        if "[Y/N]" in output:
            net_connect.send_command_timing("N", strip_prompt=False, strip_command=False)

            # Enter system-view mode
            net_connect.send_command("system-view", expect_string=r'[\[\(][a-zA-Z0-9\-\ ]+[\)\]]')

            # Execute the password change commands
            for cmd in password_change_commands:
                result = net_connect.send_command(cmd)
                logger.info(f"Command '{cmd}' executed successfully on {task.host.name}")

            # Exit system-view mode
            net_connect.send_command("quit", expect_string=r'[>]')

            # Log task completion
            write_to_csv(task.host.name, task.host.hostname, "Task completed")
        else:
            logger.info(f"No password change prompt detected on {task.host.name}")

        # Run the display transceiver diagnos interface command
        command = "display transceiver diagnos interface"
        result = net_connect.send_command(command)
        logger.info(f"Command '{command}' executed successfully on {task.host.name}")
        command_executed = True

        # Extract required information using regular expressions
        interface_pattern = re.compile(r'(\S+) transceiver diagnostic information:')
        rx_power_pattern = re.compile(r'RX power\(dBm\)\s+(-?\d+\.\d+)')

        interfaces = interface_pattern.findall(result)
        rx_powers = rx_power_pattern.findall(result)

        if len(interfaces) == len(rx_powers):
            for interface, rx_power in zip(interfaces, rx_powers):
                print(f"Result for {task.host.name}:")
                print(f"Interface: {interface}")
                print(f"RX Power (dBm): {rx_power}")

                # Write the output to CSV
                write_to_csv(task.host.name, task.host.hostname, "Command Output", "", interface, rx_power)
                logger.info(f"Writing content to CSV for {task.host.name}")
        else:
            logger.error(f"Mismatch in the number of interfaces and RX power levels for {task.host.name}")
            write_to_csv(task.host.name, task.host.hostname, "Error", "Mismatch in the number of interfaces and RX power levels")

    except Exception as e:
        error_message = str(e)
        if "Authentication failure" in error_message:
            logger.error(f"Authentication failed for {task.host.name}: Incorrect username or password")
            write_to_csv(task.host.name, task.host.hostname, "Authentication failed", "Incorrect username or password")
            authentication_failed = True
        elif "timed out" in error_message:
            logger.error(f"Connection timed out for {task.host.name}")
            write_to_csv(task.host.name, task.host.hostname, "Connection timed out", "Connection timed out")
        else:
            logger.error(f"Failed to handle password change on {task.host.name}: {e}")
            write_to_csv(task.host.name, task.host.hostname, "Error", extract_error_message(error_message))

    if not command_executed and not authentication_failed:
        write_to_csv(task.host.name, task.host.hostname, "No password change prompt detected")

    return None

def write_to_csv(hostname, ip_address, status, message="", interface="", rx_power=""):
    csv_file = 'optical_power.csv'
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(csv_file) == 0:
            writer.writerow(["Hostname", "IP Address", "Status", "Message", "Interface", "RX Power (dBm)"])
        writer.writerow([hostname, ip_address, status, message, interface, rx_power])

def extract_error_message(error_message):
    # Extract the relevant part of the error message
    lines = error_message.splitlines()
    return lines[0]  # Return the first line of the error message

# Filter the devices and run the task
result = nr.filter(F(groups__contains="hp_comware")).run(task=handle_password_change_and_run_command)

print("Task completed")

# Process the CSV file to remove redundant entries
def remove_redundant_entries(csv_file):
    with open(csv_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Get the header row
    header = rows[0]

    # Get the index of the "Hostname" and "Status" columns
    hostname_index = header.index("Hostname")
    status_index = header.index("Status")

    # Filter out redundant entries
    filtered_rows = []
    authentication_failed_hosts = set()

    for row in rows[1:]:
        hostname = row[hostname_index]
        status = row[status_index]
        if status == "Authentication failed":
            authentication_failed_hosts.add(hostname)
        if hostname not in authentication_failed_hosts or status != "No password change prompt detected":
            filtered_rows.append(row)

    # Write the filtered rows back to the CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(filtered_rows)

# Remove redundant entries from the CSV file
remove_redundant_entries('optical_power.csv')
