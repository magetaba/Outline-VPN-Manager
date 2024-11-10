# Outline VPN Manager

**Outline VPN Manager** is a Python3 script that simplifies the management of users and access URLs for an Outline VPN server. With this tool, you can create, retrieve, and manage access URLs, set expiration dates for users, and automate expiration check with cronjob, all through a command-line interface.

## Data Encryption with Yopass
This script uses the [Yopass](https://yopass.se) API to enhance security by encrypting access URLs. Yopass provides secure, one-time download URLs, so the encrypted data can be accessed only once, reducing the risk of unauthorized access. This approach ensures that your sensitive information is protected during transmission and access.

## Main Menu

When you run the script, the main menu appears, providing various options:

```plaintext
==========Outline VPN Manager==========
============== Main Menu ==============
1. Create a new access key
2. List database access keys
3. List server access keys
4. Get access URL by ID
5. Update expire date by ID
6. Delete access key by ID
7. Create expire date handler cronjob
8. Get installation output
0. Exit
============ By: Magetaba =============
Enter your choice:
```

## Menu Options
**1. Create a new access key:** 

Generate a new access URL for a user and set an expiration date.

**2. List database access keys:** 

Display all access keys stored in the SQLite database.

**3. List server access keys:** 

Retrieve and list access keys directly from the Outline VPN server.

**4. Get access URL by ID:** 

Look up and display the access URL details for a specific ID.

**5. Update expire date by ID:** 

Update the expiration date for an existing access URL by its ID.

**6. Delete access key by ID:** 

Remove an access key from the database and server.

**7. Create expire date handler cronjob:** 

Set up a cron job to manage expiration dates automatically.

**8. Get installation output:** 

Retrieve the installation output for the Outline Manager to verify the setup.

**0. Exit:** 

Close the Outline VPN Manager.

## Features
**User and Access URL Management:**

Store user details, access URLs, and expiration dates in an SQLite3 database.

**Outline Server Integration:**

Retrieve data directly from the Outline VPN server for seamless syncing.

**Expiration Date Management:**

Set and update expiration dates for each access URL and user.

**Access URL Cleanup:**

Easily delete expired or unnecessary access URLs.

**Outline Manager Installation Output:**

Retrieve installation output for the official Outline Manager app.

**Automated Cronjob Scheduler:**

Automatically create cron jobs to manage expiration checks and other maintenance tasks.

**Root Access Integration:**

Script is optimized to run with root access on your Outline VPN server.

## Prerequisites
Python 3.x
SQLite3 (comes pre-installed with Python)
Outline VPN server with root access

## Installation
**1. Clone the Repository:**
```
git clone https://github.com/magetaba/Outline-VPN-Manager.git
cd Outline-VPN-Manager
```

**2. Install Required Packages:**
```
pip install -r requirements.txt
```

**3. Configure Permissions (if needed):**
Ensure the script has permission to execute with root access on your Outline VPN server.
```
sudo chmod +x outline-vpn-manager.py
sudo chmod +x yopass.sh
```

## Usage
**To run the Outline VPN Manager, simply use:**
```
python3 outline_vpn_manager.py
```

## Future Improvements
Planned Features

**Email Notifications:** Send users automated reminders before their access expires.

**Server-Database Sync:** For users who existed on the Outline server before using this script, enable data synchronization between the database and server.


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
