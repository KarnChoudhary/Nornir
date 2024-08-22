from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import logging
import json

nr = InitNornir(config_file="config.yaml")
command = "display version"
#command = "copy running-config tftp://192.168.74.109/"
print(command)
def netmiko_send_commands_example(task):
    result = task.run(task=netmiko_send_command, command_string=command)
    # Extracting relevant information from the result
    output = result[0].result
    return {task.host.name: output}

results = nr.run(task=netmiko_send_commands_example)

print_result(results)
#print("type(results)- >",type(results))


    
# for hostname, multi_result in results.items():
#     print(results.items())
#     print("type(results.items()", results.items())
#     print("ssss-->", multi_result.result)
#     for result in multi_result.result:
#         print("----"*20)

#         print(result)
#         command_output = result.get("display lldp neighbor-info list")
#         # Process the command_output as needed (e.g., print, store in a variable)
#         print(f"Hostname: {hostname}, Output: {command_output}")
#         print("----"*20)

    
