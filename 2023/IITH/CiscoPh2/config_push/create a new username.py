from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
import re
import logging

# Configure logging with less verbose output
logging.basicConfig(
    filename='nornir_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Define users with their privileges and passwords
users_to_create = [
    {"username": "iith", "privilege": 15, "password": "RCC@IITH2022"},
    {"username": "test1", "privilege": 15, "password": "test1"},
    {"username": "test2", "privilege": 5, "password": "test2"}
]

def create_users(task):
    """Create multiple users with specified privileges"""
    try:
        for user in users_to_create:
            commands = [
                f"username {user['username']} privilege {user['privilege']} secret {user['password']}"
            ]
            result = task.run(
                task=netmiko_send_config,
                config_commands=commands,
                read_timeout=30
            )
            if result[0].failed:
                logging.error(f"Failed to create user {user['username']} on {task.host.name}: {result[0].exception}")
            else:
                logging.info(f"Successfully created user {user['username']} on {task.host.name}")
        return result
    except Exception as e:
        logging.error(f"Exception while creating users on {task.host.name}: {str(e)}")
        raise

def remove_existing_users(task):
    """Remove existing users except the ones in users_to_create"""
    try:
        # Get current users
        result = task.run(
            task=netmiko_send_command,
            command_string="show running-config | include username",
            read_timeout=30
        )
        
        if result[0].failed:
            logging.error(f"Failed to get user list on {task.host.name}")
            return
            
        output = result[0].result
        usernames = re.findall(r'username (\S+)', output)
        
        # Filter users to remove (exclude users_to_create)
        allowed_usernames = [user["username"] for user in users_to_create]
        users_to_remove = [user for user in usernames if user not in allowed_usernames]
        
        if not users_to_remove:
            logging.info(f"No users to remove on {task.host.name}")
            return
            
        # Remove users with confirmation handling
        for user in users_to_remove:
            commands = [
                f"no username {user}",
                "\n"  # Send newline to confirm the prompt
            ]
            
            result = task.run(
                task=netmiko_send_config,
                config_commands=commands,
                read_timeout=30,
                enter_config_mode=True,
                exit_config_mode=True,
                cmd_verify=False  # Disable command echo verification
            )
            
            if result[0].failed:
                logging.error(f"Failed to remove user {user} on {task.host.name}")
            else:
                logging.info(f"Successfully removed user {user} on {task.host.name}")
        
        return result
        
    except Exception as e:
        logging.error(f"Exception while removing users on {task.host.name}: {str(e)}")
        raise

def main():
    try:
        # Create new users first
        print("Creating new users...")
        result = nr.run(task=create_users)
        print_result(result)
        
        # Then remove existing users except the ones we just created
        print("Removing other existing users...")
        result = nr.run(task=remove_existing_users)
        print_result(result)
        
        print("Operations completed successfully")
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        logging.error(f"Script failed: {str(e)}")

if __name__ == "__main__":
    main()