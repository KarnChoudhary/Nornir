import os, json
import csv
os.system("clear")
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from collections import OrderedDict
#from nornir.plugins.functions.text import print_result
import nornir_utils.plugins.functions as fns
import pathlib
import logging
import datetime

g = "get_config"

def backup_configurations(task):
    config_dir = "config-archive"
    date_dir = config_dir + "/" + str(datetime.datetime.now())
    pathlib.Path(config_dir).mkdir(exist_ok=True)
    pathlib.Path(date_dir).mkdir(exist_ok=True)
    r = task.run(task=napalm_get, getters=[g])
    task.run(
        task=fns.write_file,
        content=r.result["config"]["running"],
        filename=f"" + str(date_dir) + "/" + task.host.name + ".txt",
    )


nr = InitNornir(config_file="config.yaml")
result = nr.run(name="Creating Backup Archive", task=backup_configurations)
print_result(result)




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