# bonappeti
## HTTP 401 Unauthorized - Mass Brute Force
This Python script runs the shef command for many ports, creates a directory for each and tries different passwords to gain access. 
It runs `50` brute force tasks at once using threads and adds delays for 3 seconds after executing `shef` 5 times to keep it safe.
Number of tasks can be modified in `max_concurrent_ports`.
Education purposes only. Do not use the tool with a harmful intent. 

## Usage
1. Install Shef: https://github.com/1hehaq/shef
2. Make you Shodan search `country:<change> '401'` and grab all the results showing the number of hosts associated with a certain port
3. Paste the results to `unfiltered.txt`
4. Use `filter.py` to filter the ports if needed. It will create `ports.txt`
5. Create `ports.txt` in the directory, if you did not use `filter.py`
6. Edit `bruteforce.py` script to fit your Shodan seach needs, but dont touch the port (`["shef", "-q", f"country:<change> '401' port:{port}"]`)
7. Run `bruteforce.py`: `nohup python3 bruteforce.py > bruteforce.log 2>&1 &`

Successful attempts will be output in `success.txt`. To filter false positives use `cat success.txt | grep -v false`

### `filter.py`
Filters out the number of hosts associated with ports when directly copied from Shodan. 
Example: 
`80
10213
443
17381
8080
1986` to `80
443
8080`

1. Run `python3 filter.py unfiltered.txt`

### `lookup.py`
Performs tab name grabbing. Helps you to understands whats behind those 401s
1. Run `python3 lookup.py`
