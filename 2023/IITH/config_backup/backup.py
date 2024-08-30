import os, json
import csv
os.system("clear")
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from collections import OrderedDict
#from nornir.plugins.functions.text import print_result
from nornir_utils.plugins.functions import write_file 
import pathlib
import logging   

g = "get_config"

def backup_configurations(task):
    config_dir = "config-archive"
    date_dir = config_dir + "/" + str(date.today())
    pathlib.Path(config_dir).mkdir(exist_ok=True)
    pathlib.Path(date_dir).mkdir(exist_ok=True)
    r = task.run(task=napalm_get, getters=[g])
    task.run(
        task=write_file,
        content=r.result["config"]["running"],
        filename=f"" + str(date_dir) + "/" + task.host.name + ".txt",
    )


# def nornir_napalm_get_example(task):
#     #read_time_override = 1000
#     #task.run(task=napalm_get, getters=["get_facts", "get_interfaces", "get_interfaces_ip", "get_config"])
#     task.run(task=napalm_get, getters=[g])
#     #task.run(task=napalm_get, getters=["get_snmp_information"])
#     #task.run(task=napalm_get, getters=["get_ntp_servers"])

nr = InitNornir(config_file="config.yaml")
result = nr.run(name="Creating Backup Archive", task=backup_configurations)
print_result(result)


# a = (str(print_result(results)))
# filename = "optics.csv"
# lines = []
# lines.append(["Interface", "Switch", "Instant Input Power"])
# print("-----"*8)
# for a in results.keys():
#     for b in results[a]:
#         if b.result:               
#             data = OrderedDict()
#             print("b.result", b)
#             for key, value in b.result.items():              
#                 for d, e in value.items():    
#                     if g == "get_optics":
#                         data["Interface"] = d
#                         data["Switch"] = a
#                         data["Instant Input Power"] = e['physical_channels']['channel'][0]['state']['input_power']['instant']
#                         lines.append(list(data.values()))  # Convert OrderedDict to list
#                         print(data)  # Print data in a dictionary format

# with open(filename, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(lines)

# print("Done. Check optics.csv")           


#---------------------------------------------------------------

# from nornir import InitNornir
# from nornir.plugins.tasks import networking
# from nornir.plugins.functions.text import print_result
# from nornir.plugins.tasks.files import write_file
# from datetime import date
# import pathlib

# def backup_configurations(task):
#     config_dir = "config-archive"
#     date_dir = config_dir + "/" + str(date.today())
#     pathlib.Path(config_dir).mkdir(exist_ok=True)
#     pathlib.Path(date_dir).mkdir(exist_ok=True)
#     r = task.run(task=networking.napalm_get, getters=["config"])
#     task.run(
#         task=write_file,
#         content=r.result["config"]["running"],
#         filename=f"" + str(date_dir) + "/" + task.host.name + ".txt",
#     )


# nr = InitNornir(config_file="config.yaml")


# result = nr.run(
#     name="Creating Backup Archive", task=backup_configurations
# )

# print_result(result)