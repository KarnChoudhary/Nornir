from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging
import csv
import re

# Configure logging
logging.basicConfig(filename='demo_nornir.log', level=logging.DEBUG)
logger = logging.getLogger("nornir")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the task to run the command
def run_command(task):
    command = "display version"
    result = task.run(task=netmiko_send_command, command_string=command)
    logger.info(f"Command executed successfully on {task.host.name}")
    return result

# Filter the devices and run the task
result = nr.filter(F(groups__contains="hp_comware")).run(task=run_command)

# Prepare CSV output
csv_file = 'command_output.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Hostname", "Host IP Address", "Boot Image", "Boot Image Version", "Compiled", "BOARD TYPE"])

    # Print the result and write to CSV
    for host, task_result in result.items():
        # task_result is a MultiResult object
        for sub_result in task_result:
            if sub_result.name == "netmiko_send_command":
                show_cmd = sub_result.result
                hostname = task_result.host.name
                host_ip = task_result.host.hostname

                # Extract required information using regular expressions
                boot_image = re.search(r'Boot image:\s*(.+)', show_cmd)
                boot_image_version = re.search(r'Boot image version:\s*(.+)', show_cmd)
                compiled = re.search(r'Compiled\s*(.+)', show_cmd)
                board_type = re.search(r'BOARD TYPE:\s*(.+)', show_cmd)

                boot_image = boot_image.group(1) if boot_image else "N/A"
                boot_image_version = boot_image_version.group(1) if boot_image_version else "N/A"
                compiled = compiled.group(1) if compiled else "N/A"
                board_type = board_type.group(1) if board_type else "N/A"

                print(f"Result for {hostname}:")
                print(f"Boot Image: {boot_image}")
                print(f"Boot Image Version: {boot_image_version}")
                print(f"Compiled: {compiled}")
                print(f"BOARD TYPE: {board_type}")

                # Write the output to CSV
                writer.writerow([hostname, host_ip, boot_image, boot_image_version, compiled, board_type])
                logger.info(f"Writing content to CSV for {hostname}")

print("after printing")
