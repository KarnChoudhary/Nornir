import os
import csv
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_cli
from nornir_utils.plugins.functions import print_result

# Clear the terminal
os.system("clear")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the command to be run
command = "show banner motd"

# Function to run the command
def nornir_napalm_cli_commands_example(task):
    task.run(task=napalm_cli, commands=[command])

# Run the task
results = nr.run(task=nornir_napalm_cli_commands_example)
print_result(results)

# Prepare CSV file
filename = "banner_motd_results.csv"
lines = []
lines.append(["Hostname", "Banner MOTD"])

# Process the results
for hostname, result in results.items():
    for task_result in result:
        if task_result.result:
            output = task_result.result[command]
            if output.startswith("*****************"):
                result_status = "yes"
            else:
                result_status = "no"
            lines.append([hostname, result_status])

# Write to CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print(f"Done. Check {filename}")
