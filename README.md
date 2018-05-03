<img src="https://user-images.githubusercontent.com/16360374/39081232-8f0e5384-44f2-11e8-83ac-59730ecd106a.png" height="100"/>

Everyone knows the frustration of not recieving the network performance advertised by your ISP. In response, this program aims to provide you with the data necessary to hold your ISP accountable for network downtimes and low performance.
In addition, this program can also inform you of when your network goes down, which you can potentially be credited for depending on your ISP.

## Install
If Python 3 is already installed, the program dependencies can be installed using the following command:
```sh
pip install -r requirements.txt
```

## Usage
The program can be used with optional arguments, as shown below:
```sh
python network_monitor.py [args]

optional arguments:
  -h, --help    show this help message and exit
  -c, --config  set the target download and upload speeds (mbps)
  -q, --quiet   logs network speed without output
  -g, --graph   displays a graph of data speeds for the last 30 days
  -r, --report  sends an email with a report of your network data speeds for
                the last 30 days
```


## Setup
For the most beneficial results, you should initially execute the program with the `--config` argument to set your target network upload and download speeds, as well as the email that will be used to contact you of network downtime.
Additionally, if you'd like to setup the program to run on a schedule, you can do this on UNIX-based systems by creating a cron job with the following command:

```sh
# Open your cron configuration file
crontab -e

# Schedules the program to run once an hour
0 * * * * cd /path_to_directory/network_monitor.py && python network_monitor.py -q

# Schedules a monthly report to be sent via email
0 0 1 * * cd /path_to_directory/network_monitor.py && python network_monitor.py -q -r
```
