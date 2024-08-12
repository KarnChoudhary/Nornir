import os, json
import csv
os.system("clear")
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from collections import OrderedDict

nr = InitNornir(config_file="config.yaml")

g = "get_optics"
def nornir_napalm_get_example(task):
    #read_time_override = 1000
    #task.run(task=napalm_get, getters=["get_facts", "get_interfaces", "get_interfaces_ip", "get_config"])
    task.run(task=napalm_get, getters=[g])
    #task.run(task=napalm_get, getters=["get_snmp_information"])
    #task.run(task=napalm_get, getters=["get_ntp_servers"])

results=nr.run(task=nornir_napalm_get_example)
# a = (str(print_result(results)))
filename = "optics.csv"
lines = []
lines.append(["Interface", "Switch", "Instant Input Power"])
print_result(results)
print("-----"*8)
for a in results.keys():
    for b in results[a]:
        if b.result:               
            data = OrderedDict()
            print("b.result", b.result)
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

print("Done. Check optics.csv")           

# for a in results['R1']:
#     print(a)

# from io import StringIO
# output_buffer = StringIO()
# import sys, re, json
# sys.stdout = output_buffer
# print_result(results)

# output_string = output_buffer.getvalue()
# sys.stdout = sys.__stdout__


# # Define the regex pattern to match line breaks
# line_break_pattern = r'[\r\n]+'

# # Remove all line breaks from the output string
# output_string = re.sub(line_break_pattern, ' ', output_string)

# # Define the regex pattern to match the desired substring
# pattern = r'- INFO(.*?)\^+\s+END'

# # Find all matches of the pattern in the output string
# matches = re.findall(pattern, output_string, re.DOTALL)

# # Concatenate all matches into a single string
# result_string = "".join(match.strip() for match in matches)

# # Replace single quotes with double quotes
# result_string = result_string.replace("'", '"').replace(" ", "")

# #print(result_string)
# # '''

# data33 =str(result_string).strip()
# print(data33)
# with open("m.txt", "w+") as p:
#     p.write(data33)

# # data2 = re.compile(r'[\x00-\x1f\x7f-\x9f]').sub('', data33)

# # data = json.loads(data2[:-7])

# # interface_names = []
# # for d in data:
# #     print(d)
# #     # interface_names.append(d)

# # Get the interface name from the key
# # interface_name = list(data['get_optics'].keys())[0]
# # print(interface_name)
# '''
# # Extract the input_power instant value
# input_power_instant = data['get_optics'][interface_name]['physical_channels']['channel'][0]['state']['input_power']['instant']

# print(f"Interface Name: {interface_name}")
# print(f"Input Power (Instant): {input_power_instant}")
# '''

# # print(json.loads(str(result_string).strip()))
# # # Loop through all interfaces in 'get_optics'
# # for interface_name in data.get['get_optics'].keys():  # Use keys() to get interface names
# #   interface_data = data['get_optics'][interface_name]
# #   # Extract input_power instant value
# #   input_power_instant = interface_data['physical_channels']['channel'][0]['state']['input_power']['instant']
# #   print(f"Interface Name: {interface_name}")
# #   print(f"Input Power (Instant): {input_power_instant}")
# #   print("-" * 20)  # Separator between interfaces