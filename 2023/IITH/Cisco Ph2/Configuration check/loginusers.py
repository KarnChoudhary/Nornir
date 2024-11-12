import os
import csv
import re
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_cli
from nornir_utils.plugins.functions import print_result

# Clear the terminal
os.system("clear")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the command to be run
command = "show running-config | i username"

# Function to run the command
def nornir_napalm_cli_commands_example(task):
    task.run(task=napalm_cli, commands=[command])

# Run the task
results = nr.run(task=nornir_napalm_cli_commands_example)
print_result(results)

# Prepare CSV file
filename = "username_results.csv"
lines = []
lines.append(["Hostname", "Username"])

# Regex pattern to extract the username
username_pattern = re.compile(r'username (\S+)')

# Process the results
for hostname, result in results.items():
    for task_result in result:
        if task_result.result:
            output = task_result.result[command]
            # Find all matches of the username pattern
            matches = username_pattern.findall(output)
            for username in matches:
                lines.append([hostname, username])

# Write to CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print(f"Done. Check {filename}")
