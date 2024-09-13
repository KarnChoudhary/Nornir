from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging

# Configure logging
logging.basicConfig(filename='demo_nornir.log', level=logging.DEBUG)
logger = logging.getLogger("nornir")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define the task to run the command
def run_command(task):
    result = task.run(task=netmiko_send_command, command_string="display version")
    logger.info(f"Command executed successfully on {task.host.name}")
    return result

# Filter the devices and run the task
result = nr.filter(F(groups__contains="hp_comware")).run(task=run_command)

# Print the result
for host, task_result in result.items():
    # task_result is a MultiResult object
    for sub_result in task_result:
        if sub_result.name == "netmiko_send_command":
            show_cmd = sub_result.result
            print(f"Result for {host}:")
            print(show_cmd)
            print(type(show_cmd))

            # Write the output to a file
            with open(f'sh_output_{host}.txt', 'w') as file:
                logger.info(f"Writing content to file for {host}")
                file.write(show_cmd)

print("after printing")
