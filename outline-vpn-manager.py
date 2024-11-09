import requests
import sqlite3
import os
import time
import json
import uuid
from datetime import datetime
import subprocess
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Database setup
db_connection = sqlite3.connect('vpn_manager.db')
cursor = db_connection.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier TEXT,
        name TEXT,
        password TEXT,
        port TEXT,
        method TEXT,
        expire_date TEXT,
        access_url TEXT
    )
''')
db_connection.commit()

def clear_screen():
    # Clear the screen based on the OS
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to retrieve installation output from access.txt file
def get_installation_output():
    apiUrl = ""
    certSha256 = ""
    try:
        with open('/opt/outline/access.txt', 'r') as file:
            for line in file:
                if line.startswith("apiUrl:"):
                    apiUrl = line.split(":", 1)[1].strip()
                if line.startswith("certSha256:"):
                    certSha256 = line.split(":", 1)[1].strip()

        installationOutput = f"""
        {{"apiUrl":"{apiUrl}","certSha256":"{certSha256}"}}
        """
        print(installationOutput)
    except FileNotFoundError:
        print("Error: /opt/outline/access.txt not found.")
    except Exception as e:
        print(f"Error reading: {e}")
    return None


# Function to retrieve BASE_URL from access.txt file
def get_base_url():
    try:
        with open('/opt/outline/access.txt', 'r') as file:
            for line in file:
                if line.startswith("apiUrl:"):
                    return line.split(":", 1)[1].strip()
    except FileNotFoundError:
        print("Error: /opt/outline/access.txt not found.")
    except Exception as e:
        print(f"Error reading BASE_URL: {e}")
    return None

# Function to retrieve DEFAULT_PORT from shadowbox_server_config.json file
def get_default_port():
    try:
        with open('/opt/outline/persisted-state/shadowbox_server_config.json', 'r') as file:
            config = json.load(file)
            return config.get("portForNewAccessKeys")
    except FileNotFoundError:
        print("Error: shadowbox_server_config.json not found.")
    except Exception as e:
        print(f"Error reading DEFAULT_PORT: {e}")
    return None

# Fetch BASE_URL and DEFAULT_PORT
BASE_URL = get_base_url()
DEFAULT_PORT = get_default_port()

if not BASE_URL or not DEFAULT_PORT:
    print("Failed to retrieve BASE_URL or DEFAULT_PORT. Exiting...")
    exit(1)

HEADERS = {
    "Content-Type": "application/json"
}
DEFAULT_METHOD = "chacha20-ietf-poly1305"
DATA_LIMIT_BYTES = 1000000000 * 50

def create_access_key():
    identifier = input("Enter Identifier: ")
    name = input("Enter name for the access key: ")
    expire_date = input("Enter expire date (yyyy-mm-dd): ")
    password = str(uuid.uuid4())

    payload = {
        "method": DEFAULT_METHOD,
        "name": name,
        "password": password,
        "port": DEFAULT_PORT,
        "limit": {"bytes": DATA_LIMIT_BYTES}
    }

    apiCall = "access-keys"
    url = f"{BASE_URL}/{apiCall}/{identifier}"
    response = requests.put(url, headers=HEADERS, json=payload, verify=False)
    
    if response.status_code in [200, 201]:
        response_data = response.json()
        access_url = response_data.get("accessUrl")
        
        cursor.execute('''
            INSERT INTO access_keys (identifier, name, password, port, method, expire_date, access_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (identifier, name, password, DEFAULT_PORT, DEFAULT_METHOD, expire_date, access_url))
        db_connection.commit()

        print("Access key created successfully and saved to database.")
        print(f"ID: {identifier}")
        print(f"Name: {name}")
        
        # Execute the bash command for accessing URL securely
        try:
            bash_command = f"bash /root/yopass.sh \"{access_url}\""
            output = subprocess.check_output(bash_command, shell=True, stderr=subprocess.STDOUT)
            output_str = output.decode('utf-8').strip()
            print(f"Access URL: {output_str}")
            print(f"Expire Date: {expire_date}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing bash command: {e.output.decode()}")

    else:
        print(f"Failed to create access key. Status code: {response.status_code}")

def list_access_keys():
    cursor.execute("SELECT * FROM access_keys")
    keys = cursor.fetchall()
    if keys:
        for key in keys:
            print(f" ID: {key[1]} \r\n Name: {key[2]} \r\n Password: {key[3]} \r\n Port: {key[4]} \r\n Method: {key[5]} \r\n Expire Date: {key[6]} \r\n Access URL: {key[7]}")
            print("====================================================")
    else:
        print("No access keys found.")

def list_server_access_keys():
    apiCall = "access-keys"
    url = f"{BASE_URL}/{apiCall}"
    response = requests.get(url, headers=HEADERS, verify=False)

    if response.status_code in [200, 201]:
        # Print the JSON in human-readable format
        print(json.dumps(response.json(), indent=4))
    else:
        print("Failed to retrieve server access keys.")

def delete_access_key_by_id():
    key_id = input("Enter the identifier for the access key: ")
    confirm = input("You are deleting an access key, Are you absolutely sure? [y/n]: ")

    if confirm == "y":
        apiCall = "access-keys"
        url = f"{BASE_URL}/{apiCall}/{key_id}"
        response = requests.delete(url, headers=HEADERS, verify=False)

        if response.status_code == 204:
            cursor.execute("DELETE FROM access_keys WHERE identifier = ?", (key_id,))
            print(f"Access Key for ID {key_id} Deleted Successfully.")
        else:
            print("Error deleting access key from server.")
    else:
        print("Deletion canceled.")
    
def create_cronjob_expiredate():

    script_content = """
import requests
import sqlite3
from datetime import datetime
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Database setup
db_connection = sqlite3.connect('vpn_manager.db')
cursor = db_connection.cursor()

# Function to retrieve BASE_URL from access.txt file
def get_base_url():
    try:
        with open('/opt/outline/access.txt', 'r') as file:
            for line in file:
                if line.startswith("apiUrl:"):
                    return line.split(":", 1)[1].strip()
    except FileNotFoundError:
        print("Error: /opt/outline/access.txt not found.")
    except Exception as e:
        print(f"Error reading BASE_URL: {e}")
    return None

# Constants
BASE_URL = get_base_url()

if not BASE_URL:
    print("Failed to retrieve BASE_URL or DEFAULT_PORT. Exiting...")
    exit(1)

HEADERS = {
    "Content-Type": "application/json"
}
DATA_LIMIT_BYTES = 10000  # 10 KB limit for expired keys

# Logging setup
logging.basicConfig(
    filename='vpn_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_and_update_expired_keys():
    # Get today's date
    today_date = datetime.now().date()

    # Fetch all keys with an expire_date before today's date
    cursor.execute("SELECT identifier, expire_date FROM access_keys WHERE expire_date <= ?", (today_date,))
    expired_keys = cursor.fetchall()

    if expired_keys:
        for key in expired_keys:
            identifier = key[0]
            expire_date = key[1]

            # URL to set the data limit for the expired access key
            url = f"{BASE_URL}/access-keys/{identifier}/data-limit"

            # Set data limit payload
            payload = {
                "limit": {"bytes": DATA_LIMIT_BYTES}
            }

            # Send request to set data limit
            response = requests.put(url, headers=HEADERS, json=payload, verify=False)

            if response.status_code == 204:
                logging.info(f"Data limit set for expired key (ID: {identifier}, Expire Date: {expire_date})")
            else:
                logging.error(f"Failed to set data limit for key {identifier}. Status code: {response.status_code}")
    else:
        logging.info("No expired access keys found.")

if __name__ == "__main__":
    check_and_update_expired_keys()
    # Close the database connection when done
    db_connection.close()
"""

    with open("/root/outline_expired.py", "w") as file:
        file.write(script_content)

    # Make the file executable
    os.chmod("/root/outline_expired.py", 0o755)

    cron_command = "python3 /root/outline_expired.py"
    cron_schedule = "0 */5 * * *"
    cron_job = f"{cron_schedule} {cron_command}\n"

    with open("/tmp/crontab.tmp", "w") as f:
        existing_cron = os.popen("crontab -l").read()
        f.write(existing_cron)
        
        if cron_job not in existing_cron:
            f.write(cron_job)

    os.system("crontab /tmp/crontab.tmp")
    os.remove("/tmp/crontab.tmp")

    print("Cron job added successfully.")

def get_access_url_by_id():
    key_id = input("Enter the identifier for the access key: ")
    cursor.execute("SELECT access_url FROM access_keys WHERE identifier = ?", (key_id,))
    result = cursor.fetchone()
    
    if result:
        access_url = result[0]
        try:
            bash_command = f"bash /root/yopass.sh \"{access_url}\""
            output = subprocess.check_output(bash_command, shell=True, stderr=subprocess.STDOUT)
            output_str = output.decode('utf-8').strip()
            print(f"Access URL for ID {key_id}: {output_str}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing bash command: {e.output.decode()}")
    else:
        print("Access key not found with the provided ID.")

def update_expire_date():
    key_id = input("Enter the identifier for the access key to update: ")
    new_expire_date = input("Enter the new expire date (yyyy-mm-dd): ")

    url = f"{BASE_URL}/access-keys/{key_id}/data-limit"
    
    cursor.execute("UPDATE access_keys SET expire_date = ? WHERE identifier = ?", (new_expire_date, key_id))
    db_connection.commit()

    if cursor.rowcount > 0:
        print(f"Expire date updated successfully for ID {key_id}.")
    else:
        print("Access key not found with the provided ID.")

    payload = {
        "limit": {"bytes": DATA_LIMIT_BYTES}
    }

    response = requests.put(url, headers=HEADERS, json=payload, verify=False)

    if response.status_code == 204:
        print(f"Data limit reset for updated key (ID: {key_id}, Expire Date: {new_expire_date})")
    else:
        print(f"Failed to reset data limit for key {key_id}. Status code: {response.status_code}")

def show_menu():
    print("==========Outline VPN Manager==========")
    print("============== Main Menu ==============")
    print("1. Create a new access key")
    print("2. List database access keys")
    print("3. List server access keys")
    print("4. Get access URL by ID")
    print("5. Update expire date by ID")
    print("6. Delete access key by ID")
    print("7. Create expire date handler cronjob")
    print("8. Get installation output")
    print("0. Exit")
    print("============ By: Magetaba =============")


def menu():
    while True:
        clear_screen()
        show_menu()
        
        try:
            choice = input("Enter your choice: ")
            
            if choice == '1':
                create_access_key()
            elif choice == '2':
                list_access_keys()
            elif choice == '3':
                list_server_access_keys()
            elif choice == '4':
                get_access_url_by_id()
            elif choice == '5':
                update_expire_date()
            elif choice == '6':
                delete_access_key_by_id()
            elif choice == '7':
                create_cronjob_expiredate()
            elif choice == '8':
                get_installation_output()
            elif choice == '0':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

            # Prompt for confirmation before returning to the main menu
            input("\nPress Enter to return to the main menu...")

        except ValueError:
            print("\nPlease enter a valid number.")
            input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    menu()

# Close database connection
db_connection.close()
