import os, json
import csv
import logging
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from collections import OrderedDict

os.system("clear")

nr = InitNornir(config_file="config.yaml")

# Define the commands and getters
command1 = "show interfaces trans"
g = "get_optics"

def nornir_napalm_get_example(task):
    task.run(task=napalm_get, getters=[g])

def netmiko_show_int_trans(task):
    result = task.run(task=netmiko_send_command, command_string=command1, read_timeout=1000000)
    output = result[0].result
    return {task.host.name: output}

# Define a function to determine the switch type and run the appropriate task
def get_fiber_power_level(task):
    if "Dist" in task.host.name:  # Assuming 'Dist' in the name for distribution switches
        return netmiko_show_int_trans(task)
    else:  # Assuming other platforms for access switches
        return nornir_napalm_get_example(task)

results = nr.run(task=get_fiber_power_level)

# Prepare CSV file
filename = "fiber power level.csv"
lines = [["Interface", "Switch", "Instant Input Power"]]

print_result(results)
print("-----"*8)

for a in results.keys():
    for b in results[a]:
        if b.result:
            if "Dist" in a:  # Distribution switch
                data = OrderedDict()
                val = str(b.result).split("--------\n")[-1]
                val = val.split("   \n")

                print("--x---x-"*20)
                print("Port,", "Optical Rx Power (dBm)")

                for v in val:
                    if "device is externally calibrated" in str(v):
                        continue

                    v = v.split("     ")
                    if len(v) > 5:
                        aaaaa = [str(v[0]).split("  ")[0].strip(), a, str(v[-1]).strip()]
                        print(aaaaa)
                        lines.append(aaaaa)
            else:  # Access switch
                data = OrderedDict()
                for key, value in b.result.items():
                    for d, e in value.items():
                        if g == "get_optics":
                            data["Interface"] = d
                            data["Switch"] = a
                            data["Instant Input Power"] = e['physical_channels']['channel'][0]['state']['input_power']['instant']
                            lines.append(list(data.values()))  # Convert OrderedDict to list
                            print(data)  # Print data in a dictionary format

# Write to CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print("Done. Check fiber power level.csv")
