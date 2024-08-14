import os, json
import csv, logging, napalm
os.system("clear")

from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from collections import OrderedDict
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

#driver = napalm.get_network_driver('ios')
#device = driver('10.4.124.1', 'iith', 'CC@IITH2022', optional_args={'read_timeout_override': 600})

nr = InitNornir(config_file="config.yaml")
command1 = "show interfaces trans"
#command = "copy running-config tftp://192.168.74.109/"
# print(command1)
def netmiko_show_int_trans(task):
    result = task.run(task=netmiko_send_command, command_string=command1, read_timeout= 1000000)
    # Extracting relevant information from the result
    output = result[0].result
    return {task.host.name: output}

results = nr.run(task=netmiko_show_int_trans)
filename = "opticsm.csv"
lines = []
lines.append(["Interface", "Switch", "Instant Input Power"])
print_result(results)
for a in results.keys():
    # print("a is = ",a)
    for b in results[a]:
        if b.result:
            data = OrderedDict()
                      
            val = str(b.result).split("--------\n")[-1]
            val = val.split("   \n")
            # print("b.result in string format =",val)

            print("--x---x-"*20)
            print("Port,", "Optical Rx Power (dBm)")

            for v in val:
                if "device is externally calibrated" in str(v):
                    continue

                v = v.split("     ")                
                if len(v)>5:                    
                    aaaaa = [str(v[0]).split("  ")[0].strip(),a,str(v[-1]).strip()]
                    print(aaaaa)
                    lines.append(aaaaa)
            
                
               
    
with open(filename, mode='w+', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print("end of code")
