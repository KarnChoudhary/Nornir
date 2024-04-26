from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import logging

nr = InitNornir(config_file="config.yaml")
command = "display lldp neighbor-info list"

def netmiko_send_commands_example(task):
    result = task.run(task=netmiko_send_command, command_string=command)
    output = result[0].result

    # Extract local interface and system name
    neighbors = []
    header_found = False  # Flag to track header row
    for line in output.splitlines():
        if line.startswith("Local Interface"):
            header_found = True
            continue

        if header_found:
            try:
                interface, _, system_name = line.split()
                neighbors.append({
                    "local_interface": interface,
                    "system_name": system_name
                })
            except ValueError:  # Handle cases where all data might not be present
                pass

    return {task.host.name: neighbors}

results = nr.run(task=netmiko_send_commands_example)
print_result(results)
