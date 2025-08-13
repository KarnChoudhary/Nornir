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

        # Run the display device manuinfo command
        command = "display device manuinfo"
        result = net_connect.send_command(command)
        logger.info(f"Command '{command}' executed successfully on {task.host.name}")
        command_executed = True

        # Extract required information using regular expressions
        device_name = re.search(r'DEVICE_NAME\s*:\s*(.+)', result)
        device_serial_number = re.search(r'DEVICE_SERIAL_NUMBER\s*:\s*(.+)', result)
        mac_address = re.search(r'MAC_ADDRESS\s*:\s*(.+)', result)
        manufacturing_date = re.search(r'MANUFACTURING_DATE\s*:\s*(.+)', result)
        vendor_name = re.search(r'VENDOR_NAME\s*:\s*(.+)', result)

        device_name = device_name.group(1).strip() if device_name else "N/A"
        device_serial_number = device_serial_number.group(1).strip() if device_serial_number else "N/A"
        mac_address = mac_address.group(1).strip() if mac_address else "N/A"
        manufacturing_date = manufacturing_date.group(1).strip() if manufacturing_date else "N/A"
        vendor_name = vendor_name.group(1).strip() if vendor_name else "N/A"

        print(f"Result for {task.host.name}:")
        print(f"Device Name: {device_name}")
        print(f"Device Serial Number: {device_serial_number}")
        print(f"MAC Address: {mac_address}")
        print(f"Manufacturing Date: {manufacturing_date}")
        print(f"Vendor Name: {vendor_name}")

        # Write the output to CSV
        write_to_csv(task.host.name, task.host.hostname, device_name=device_name, device_serial_number=device_serial_number, mac_address=mac_address, manufacturing_date=manufacturing_date, vendor_name=vendor_name)

    except Exception as e:
        error_message = str(e)
        if "Authentication failure" in error_message:
            logger.error(f"Authentication failed for {task.host.name}: Incorrect username or password")
            write_to_csv(task.host.name, task.host.hostname, status="Authentication failed", message="Incorrect username or password")
            authentication_failed = True
        elif "timed out" in error_message:
            logger.error(f"Connection timed out for {task.host.name}")
            write_to_csv(task.host.name, task.host.hostname, status="Connection timed out", message="Connection timed out")
        else:
            logger.error(f"Failed to handle password change on {task.host.name}: {e}")
            write_to_csv(task.host.name, task.host.hostname, status="Error", message=extract_error_message(error_message))

    if not command_executed and not authentication_failed:
        write_to_csv(task.host.name, task.host.hostname, status="No password change prompt detected")

def write_to_csv(hostname, ip_address, status="", message="", device_name="", device_serial_number="", mac_address="", manufacturing_date="", vendor_name=""):
    csv_file = 'device_manuinfo.csv'
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(csv_file) == 0:
            writer.writerow(["Hostname", "IP Address", "Status", "Message", "Device Name", "Device Serial Number", "MAC Address", "Manufacturing Date", "Vendor Name"])
        writer.writerow([hostname, ip_address, status, message, device_name, device_serial_number, mac_address, manufacturing_date, vendor_name])

def extract_error_message(error_message):
    # Extract the relevant part of the error message
    lines = error_message.splitlines()
    return lines[0]  # Return the first line of the error message

# Filter the devices and run the task
result = nr.filter(F(groups__contains="hp_comware")).run(task=handle_password_change_and_run_command)
print("Task completed")
