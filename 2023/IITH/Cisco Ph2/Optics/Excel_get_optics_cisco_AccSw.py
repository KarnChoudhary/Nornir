import os, json
import csv
os.system("clear")
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from collections import OrderedDict

nr = InitNornir(config_file="config.yaml")

import logging   
g = "get_optics"
def nornir_napalm_get_example(task):
    #read_time_override = 1000
    #task.run(task=napalm_get, getters=["get_facts", "get_interfaces", "get_interfaces_ip", "get_config"])
    task.run(task=napalm_get, getters=[g])
    #task.run(task=napalm_get, getters=["get_snmp_information"])
    #task.run(task=napalm_get, getters=["get_ntp_servers"])

results=nr.run(task=nornir_napalm_get_example)
# a = (str(print_result(results)))
filename = "access_sw_optics.csv"
lines = []
lines.append(["Interface", "Switch", "Instant Input Power"])
print_result(results)
print("-----"*8)
for a in results.keys():
    for b in results[a]:
        if b.result:               
            data = OrderedDict()
            print("b.result", b)
            for key, value in b.result.items():              
                for d, e in value.items():    
                    if g == "get_optics":
                        data["Interface"] = d
                        data["Switch"] = a
                        data["Instant Input Power"] = e['physical_channels']['channel'][0]['state']['input_power']['instant']
                        lines.append(list(data.values()))  # Convert OrderedDict to list
                        print(data)  # Print data in a dictionary format

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print("Done. Check access_sw_optics.csv")           





