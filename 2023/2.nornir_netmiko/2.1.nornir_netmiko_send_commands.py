# from nornir import InitNornir
# from nornir_netmiko.tasks import netmiko_send_command
# from nornir_utils.plugins.functions import print_result
# import logging

# nr = InitNornir(config_file="config.yaml")
# command=["show cdp neighbors"]

# def netmiko_send_commands_example(task):
#     #for command in commands:
#     rr = task.run(task=netmiko_send_command, command_string=command)
#     output = rr[0].result
#     return {
#         rr.host.name : output
#     }

# results=nr.run(task=netmiko_send_commands_example)
# print_result(results)

from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import logging
import json

nr = InitNornir(config_file="config.yaml")
#command = "display lldp neighbor-info list"
command = "display transceiver diagnos interface  Ten-GigabitEthernet 1/0/28"

def netmiko_send_commands_example(task):
    result = task.run(task=netmiko_send_command, command_string=command)
    # Extracting relevant information from the result
    output = result[0].result
    return {task.host.name: output}

results = nr.run(task=netmiko_send_commands_example)

print_result(results)