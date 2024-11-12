import os, json, re
import csv
os.system("clear")

from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_cli
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")
command = "show spanning-tree mst"

def nornir_napalm_cli_commands_example(task):
    task.run(task=napalm_cli, commands=[command])

results = nr.run(task=nornir_napalm_cli_commands_example)
print_result(results)

# Extract VLAN mappings for each MST instance
mst_pattern = re.compile(r'##### MST(\d+)\s+vlans mapped:\s+(.+)')

# Prepare CSV file
filename = "mst_vlan_mappings.csv"
lines = []
lines.append(["Hostname", "MST Instance", "VLANs Mapped"])

for hostname, result in results.items():
    for task_result in result:
        if task_result.result:
            output = task_result.result[command]

            # Extract MST instance and VLAN mappings
            mst_matches = mst_pattern.findall(output)

            for match in mst_matches:
                mst_instance = match[0]
                vlans_mapped = match[1]
                lines.append([hostname, f"MST{mst_instance}", vlans_mapped])

# Write to CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print(f"Done. Check {filename}")
