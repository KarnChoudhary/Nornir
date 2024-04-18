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
import json

nr = InitNornir(config_file="config.yaml")
command = "show cdp neighbors"

def netmiko_send_commands_example(task):
    result = task.run(task=netmiko_send_command, command_string=command)
    # Extracting relevant information from the result
    output = result[0].result
    return {task.host.name: output}

results = nr.run(task=netmiko_send_commands_example)

