from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging
import csv

# Configure logging
logging.basicConfig(filename='demo_nornir.log', level=logging.DEBUG)
logger = logging.getLogger("nornir")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the task to run the command
def run_command(task):
    command = "display current-configuration | begin karn | i network"
    result = task.run(task=netmiko_send_command, command_string=command)
    logger.info(f"Command executed successfully on {task.host.name}")
    return result

# Filter the devices and run the task
result = nr.filter(F(groups__contains="hp_comware")).run(task=run_command)

# Prepare CSV output
csv_file = 'command_output.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Hostname", "Host IP Address", "Command Result"])

    # Print the result and write to CSV
    for host, task_result in result.items():
        # task_result is a MultiResult object
        for sub_result in task_result:
            if sub_result.name == "netmiko_send_command":
                show_cmd = sub_result.result
                hostname = task_result.host.name
                host_ip = task_result.host.hostname
                print(f"Result for {hostname}:")
                print(show_cmd)
                print(type(show_cmd))

                # Write the output to CSV
                writer.writerow([hostname, host_ip, show_cmd])
                logger.info(f"Writing content to CSV for {hostname}")

print("after printing")
