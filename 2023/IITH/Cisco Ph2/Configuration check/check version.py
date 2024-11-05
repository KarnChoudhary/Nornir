import os, json, re
import csv
os.system("clear")

from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_cli
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")
command = "show version"

def nornir_napalm_cli_commands_example(task):
    task.run(task=napalm_cli, commands=[command])

results = nr.run(task=nornir_napalm_cli_commands_example)
print_result(results)

# Extract SW Version, SW Image, and Model
sw_version_pattern = re.compile(r'SW Version\s+(\d+\.\d+\.\d+)')
sw_image_pattern = re.compile(r'SW Image\s+(\S+)')
model_pattern = re.compile(r'Model\s+(\S+)')

# Prepare CSV file
filename = "sw_version_image.csv"
lines = []
lines.append(["Hostname", "SW Version", "SW Image", "Model"])

for hostname, result in results.items():
    for task_result in result:
        if task_result.result:
            output = task_result.result[command]

            # Extract values from the table format at the end of the output
            table_pattern = re.compile(r'Switch Ports Model\s+SW Version\s+SW Image\s+Mode\s*\n'
                                       r'------ ----- -----              ----------        ----------            ----   \s*\n'
                                       r'\*    \d+ \d+    (\S+)\s+(\d+\.\d+\.\d+)\s+(\S+)\s+INSTALL', re.MULTILINE)

            table_match = table_pattern.search(output)

            if table_match:
                model = table_match.group(1)
                sw_version = table_match.group(2)
                sw_image = table_match.group(3)
            else:
                model = "N/A"
                sw_version = "N/A"
                sw_image = "N/A"

            lines.append([hostname, sw_version, sw_image, model])

# Write to CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print(f"Done. Check {filename}")
