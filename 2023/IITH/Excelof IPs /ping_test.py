from nornir import InitNornir
from nornir.core.task import Result
from nornir_utils.plugins.functions import print_result
import socket
import csv

def check_reachability(task):
    host = task.host.hostname
    port = 22  # Default SSH port
    try:
        socket.create_connection((host, port), timeout=5)
        return Result(host=task.host, result="Yes")
    except socket.error:
        return Result(host=task.host, result="No")

def main():
    nr = InitNornir(config_file="config.yaml")
    result = nr.run(task=check_reachability)

    # Prepare CSV file
    csv_file = "reachability_results.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Hostname", "Reachable"])

        for host, task_result in result.items():
            hostname = task_result[0].host.hostname
            reachability_result = task_result[0].result
            writer.writerow([hostname, reachability_result])

    print(f"Results saved to {csv_file}")

if __name__ == "__main__":
    main()
