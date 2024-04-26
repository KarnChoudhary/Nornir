import os, json, re
os.system("clear")

from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_cli
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")

command = "display lldp neighbor-info list"

results=nr.run(task=napalm_cli, commands=[command])

print_result(results)