import os
import csv
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_cli
from nornir_utils.plugins.functions import print_result

# Clear the terminal
os.system("clear")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the commands to be run
commands = [
    "show running-config | i no ip http secure-server",
    "show running-config | i no ip http server"
]

# Define the expected results
expected_results = [
    "no ip http secure-server",
    "no ip http server"
]

# Define the labels for the CSV output
command_labels = [
    "https-disabled ?",
    "http-disabled ?"
]

# Function to run the commands
def nornir_napalm_cli_commands_example(task):
    task.run(task=napalm_cli, commands=commands)

# Run the task
results = nr.run(task=nornir_napalm_cli_commands_example)
print_result(results)

# Prepare CSV file
filename = "command_results.csv"
lines = []
lines.append(["Hostname", "Command", "Result"])

# Process the results
for hostname, result in results.items():
    for task_result in result:
        if task_result.result:
            for command, expected_result, label in zip(commands, expected_results, command_labels):
                output = task_result.result[command]
                if expected_result in output:
                    result_status = "yes"
                else:
                    result_status = "no"
                lines.append([hostname, label, result_status])

# Write to CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lines)

print(f"Done. Check {filename}")
