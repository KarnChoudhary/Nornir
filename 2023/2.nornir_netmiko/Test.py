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

import os, json
import csv
os.system("clear")
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from collections import OrderedDict

from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import logging
import json

nr = InitNornir(config_file="config.yaml")
command = "show interfaces trans"
#command = "copy running-config tftp://192.168.74.109/"
print(command)
def netmiko_send_commands_example(task):
    result = task.run(task=netmiko_send_command, command_string=command, read_timeout= 1000000)
    # Extracting relevant information from the result
    output = result[0].result
    return {task.host.name: output}

results = nr.run(task=netmiko_send_commands_example)

print_result(results)

filename = "optics.csv"
lines = []
lines.append(["Interface", "Switch", "Instant Input Power"])
#print_result(results)
print("-----"*8)
for a in results.keys():
    for b in results[a]:
        if b.result:               
            data = OrderedDict()
            print("b.result", b)
            for key, value in b.result.items():
                for d, e in value.items():
                    #if g == "get_optics":
                        data["Interface"] = d
                        data["Switch"] = a
                        data["Instant Input Power"] = e['physical_channels']['channel'][0]['state']['input_power']['instant']
                        lines.append(list(data.values()))  # Convert OrderedDict to list
                        print(data)  # Print data in a dictionary format

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print("Done. Check optics.csv")           