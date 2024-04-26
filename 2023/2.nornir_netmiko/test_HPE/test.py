from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import logging
import json

nr = InitNornir(config_file="config.yaml")

commands = ["display lldp neighbor-info list"]

def netmiko_send_commands_example(task):
        result = task.run(task=netmiko_send_command, command_string=commands)
        # Extracting relevant information from the result
        print("result -->",result)
        output = result[0].result
        x={task.host.name: output}
        print("return--- >", x)
        return {x}
        


results = nr.run(task=netmiko_send_commands_example)

print_result(results)
print("type(results)- >",type(results))


    
for hostname, multi_result in results.items():
    print(results.items())
    print("type(results.items()", results.items())
    print("ssss-->", multi_result.result)
    for result in multi_result.result:
        print("----"*20)

        print(result)
        command_output = result.get("display lldp neighbor-info list")
        # Process the command_output as needed (e.g., print, store in a variable)
        print(f"Hostname: {hostname}, Output: {command_output}")
        print("----"*20)

    
'''
    newstr = inventory.split("NAME")                               
    for n in newstr:
                text1 = "NAME" + n
                        # going to check name and desc using regex patterns
                matches1 = re.search(r'NAME: "(.*?)",\sDESCR: "(.*?)"', text1)                        
                        
                if matches1:
                    name = matches1.group(1)
                    descr = matches1.group(2)
                    sn = text1.split("SN:")[1]    # since we know that SN is in last of text1

                    if descr.startswith("C93") or descr.startswith("C95"):
                        lines.append([hostname, name,descr,sn.strip(), start_date.split("UTC")[0].strip(),end_date.split("UTC")[0].strip()])

    #lines.append([hostname, start_date,end_date])  # Unpack license info for CSV

with open(filename, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(lines)

    print(f"information written to '{filename}'.")
    '''