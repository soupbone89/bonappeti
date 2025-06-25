import requests
from requests.auth import HTTPBasicAuth

# Define input and output files
input_file = 'success.txt'
output_file = 'banners.txt'

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

print(f"""{BLUE}
This might take a while...
Pay attention to errors and retest the IPs manually if the script fails.
{RESET}""")

def grab_tab_name(ip_port, username, password):
    """
    Perform basic auth and grab the tab name from the webpage.
    """
    try:
        url = f"http://{ip_port}"  # Adjust protocol if needed (http/https)
        response = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=10)

        if response.status_code == 200:
            # Extract tab name (assumes it's in the title tag of the page)
            start = response.text.find("<title>") + len("<title>")
            end = response.text.find("</title>", start)
            return response.text[start:end] if start > len("<title>") - 1 and end != -1 else "No Tab Name Found"
        elif response.status_code == 401:
            return "Unauthorized (401)"
        else:
            return f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def filter_input_file(input_file):
    """
    Filter the input file to exclude lines with 'false' or 'Error: 401 Client Error'.
    """
    filtered_lines = []
    with open(input_file, 'r') as infile:
        for line in infile:
            if 'false' not in line and 'Error: 401 Client Error' not in line and '154.205.128.114' not in line and '38.60.221.224' not in line:
                filtered_lines.append(line.strip())
    return filtered_lines

def main():
    # Filter input file
    filtered_lines = filter_input_file(input_file)

    # Store successful results and errors separately
    successes = []
    errors = []

    # Process each filtered line
    for line in filtered_lines:
        # Parse IP:Port and credentials
        ip_port, creds = line.split(' - ')
        username, password = creds.split(':')

        # Grab the tab name
        result = grab_tab_name(ip_port, username, password)

        if "Error" in result or "Unauthorized" in result or "HTTP" in result:
            # Add to errors
            errors.append(f"{line} - {result}")
        else:
            # Add to successes
            successes.append(f"{line} - {result}")

    # Write results to the output file
    with open(output_file, 'w') as outfile:
        outfile.write("=== Successful Attempts ===\n")
        outfile.writelines(f"{success}\n" for success in successes)
        outfile.write("\n=== Errors ===\n")
        outfile.writelines(f"{error}\n" for error in errors)

    # Display successes and errors with colors
    print(f"\n{GREEN}=== Successful Attempts ==={RESET}")
    for success in successes:
        print(f"{GREEN}{success}{RESET}")
    print(f"\n{RED}=== Errors ==={RESET}")
    for error in errors:
        print(f"{RED}{error}{RESET}")

if __name__ == "__main__":
    main()
