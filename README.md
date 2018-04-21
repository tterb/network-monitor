# Network Monitor

This program is motivated by the feeling of not recieving the network performance advertised by your ISP. In response, this program aims to provide you with the data necessary to hold your ISP accountable for network downtimes and low performance.  
Additionally, this program can also inform you when your network goes down when you may not be home, which you can potentially be credited for depending on your ISP.

## Install
If Python 3 is already installed, the program dependencies can be installed using the following command:
```sh
pip install -r requirements.txt
```

## Usage
The program can be used with optional arguments, as shown below:
```sh
python network_monitor.py [-args]
```

### Arguments

| **Arguments**  | **Function**                              |
|:--------------:|-------------------------------------------|
| `-c, --config` | set the target download and upload speeds |
| `-q, --quiet`  | logs network speed without output         |
| `-g, --graph`  | creates and displays a graph of log data  |
| `-h, --help`   | displays available usage options          |


## Setup
For the most beneficial results, you should initially execute the program with the `--config` argument to set your target network upload and download speeds, which the program will then use for future processes.  
Additionally, if you'd like to setup the program to run on a schedule, you can do this on UNIX-based systems by creating a cron job with the following command:

```sh
# Open your cron configuration file
crontab -e

# Schedules the program to run once an hour
0 * * * * cd /path_to_directory/network_monitor.py && python network_monitor.py -q
```
