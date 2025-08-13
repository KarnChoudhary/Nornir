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

# Define the task to run the show system, show module, and show version commands
def run_show_commands(task):
    command_executed = False
    authentication_failed = False
    try:
        # Connect to the device
        net_connect = task.host.get_connection("netmiko", task.nornir.config)

        # Initialize variables to store extracted information
        system_name, software_version, mac_addr, serial_number, chassis_type, version = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

        # Run the show system command
        command = "show system"
        result_system = net_connect.send_command(command)
        logger.info(f"Command '{command}' executed successfully on {task.host.name}")
        command_executed = True

        # Extract required information using regular expressions
        system_name_match = re.search(r'System Name\s+:\s+(.+)', result_system)
        system_name = system_name_match.group(1).strip() if system_name_match else "N/A"

        # Extract software version
        software_version_match = re.search(r'Software revision\s+:\s+([A-Z]{2}\.\d+\.\d+\.\d+)', result_system)
        software_version = software_version_match.group(1).strip() if software_version_match else "N/A"

        # Extract information for each VSF member
        vsf_members = re.findall(r'VSF-Member\s+:\d+\s+ROM Version\s+:\s+(.+?)\s+Up Time\s+:\s+(.+?)\s+CPU Util \(%\)\s+:\s+(.+?)\s+MAC Addr\s+:\s+(.+?)\s+Serial Number\s+:\s+(.+?)\s+Memory', result_system, re.DOTALL)

        if vsf_members:
            for member in vsf_members:
                mac_addr = member[3].strip()
                serial_number = member[4].strip()
        else:
            # Handle non-VSF switches
            mac_addr_match = re.search(r'MAC Addr\s+:\s+(.+)', result_system)
            mac_addr = mac_addr_match.group(1).strip() if mac_addr_match else "N/A"

            serial_number_match = re.search(r'Serial Number\s+:\s+(.+)', result_system)
            serial_number = serial_number_match.group(1).strip() if serial_number_match else "N/A"

        # Run the show module command
        command = "show module"
        result_module = net_connect.send_command(command)
        logger.info(f"Command '{command}' executed successfully on {task.host.name}")

        # Extract required information using regular expressions
        chassis_info = re.search(r'Chassis:\s*(.+?)\s+Serial Number', result_module)
        chassis_type = chassis_info.group(1).strip() if chassis_info else "N/A"

        # Run the show version command
        command = "show version"
        result_version = net_connect.send_command(command)
        logger.info(f"Command '{command}' executed successfully on {task.host.name}")

        # Extract version information using regular expressions
        version_info = re.search(r'(WC|YC)\.\d+\.\d+\.\d+', result_version)
        version = version_info.group(0) if version_info else "N/A"

        print(f"Result for {task.host.name}:")
        print(f"System Name: {system_name}")
        print(f"Software Version: {software_version}")
        print(f"MAC Address: {mac_addr}")
        print(f"Serial Number: {serial_number}")
        print(f"Chassis Type: {chassis_type}")
        print(f"Version: {version}")

        # Write the combined output to CSV
        write_to_csv(task.host.name, task.host.hostname, "Command Output", system_name, software_version, mac_addr, serial_number, chassis_type, version)
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

def write_to_csv(hostname, ip_address, status, system_name="", software_version="", mac_addr="", serial_number="", chassis_type="", version=""):
    csv_file = 'task_status.csv'
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(csv_file) == 0:
            writer.writerow(["Hostname", "IP Address", "Status", "System Name", "Software Version", "MAC Address", "Serial Number", "Chassis Type", "Version"])
        # Write a single row with all the information
        writer.writerow([hostname, ip_address, status, system_name, software_version, mac_addr, serial_number, chassis_type, version])

def extract_error_message(error_message):
    # Extract the relevant part of the error message
    lines = error_message.splitlines()
    return lines[0]  # Return the first line of the error message

# Debug: Run the task on all devices to ensure the script works
result = nr.run(task=run_show_commands)
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
    status_index = header.index("Status")

    # Filter out redundant entries
    filtered_rows = []
    seen = set()
    for row in rows[1:]:
        hostname = row[hostname_index]
        if hostname not in seen:
            seen.add(hostname)
            filtered_rows.append(row)

    # Write the filtered rows back to the CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(filtered_rows)

# Remove redundant entries from the CSV file
remove_redundant_entries('task_status.csv')
