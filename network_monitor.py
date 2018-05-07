import sys, os, re, glob, argparse, subprocess, json, smtplib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from time import gmtime, strftime
from datetime import datetime
from email.message import EmailMessage

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--config', action="store_true", help='set the target download and upload speeds (mbps)')
  parser.add_argument('-q', '--quiet', action="store_true", help='logs network speed without output')
  parser.add_argument('-g', '--graph', action="store_true", help='displays a graph of data speeds for the last 30 days')
  parser.add_argument('-r', '--report', action="store_true", help='sends an email with a report of your network data speeds for the last 30 days')
  args = parser.parse_args()
  if args.config:
    # Set target data speeds
    target = config()
    with open('config.json','w') as f:
      json.dump(target, f, indent=2)
  elif os.path.exists('config.json'):
    # Read stored data speeds
    target = json.load(open('config.json'))
  else:
    # Create config.json with default data speeds
    target = {'download': 65, 'upload': 10}
    with open('config.json','w') as f:
      json.dump(target, f, indent=2)

  if args.quiet:
    sys.stdout = open(os.devnull, 'w')

  # Get current data speeds
  try:
    current = test_speed()
  except:
    current = (0,0)

  with open(os.getcwd()+'/log.json','r') as f:
    log = json.load(f)
  index = -1
  keys = list(log.keys())
  prev = keys[index]
  if 0 in log[prev]:
    while 0 in log[prev]:
      index -= 1
      prev = keys[index]
    print(keys[index])
    hr = datetime.strptime(keys[index].split(':')[1], "%H").strftime("%I:%M %p")
    d = [int(i) for i in keys[index].split(':')[0].split('-')]
    msg = "Your network is back online.\nWe've recorded that your network has been down since "+hr+", on "+months[d[1]]+" "+str(d[2])+"."
    print(msg)
    sendEmail(msg)
    
  # Log current data speeds
  logger(current[0], current[1])
  status = ['download','upload']
  for j,i in enumerate(status):
    print(str(i.capitalize())+': '+str(current[j])+' mbps')

  if args.graph:
    plt = create_graph()
    plt.show()
  
  if args.report:
    create_graph()
    rep = report(target)
    sendEmail(str(rep)+"\nThe following graph shows your network speed for the month", sorted([file for file in glob.glob("*.png")])[0])
    sys.exit()


def test_speed():
  speed = subprocess.check_output(['python', 'speedtest.py', '--simple']).decode()
  return tuple([float(re.findall('\d+\.\d+', i)[0]) for i in speed.splitlines()[1:]])


def config():
  if os.path.exists('config.json'):
    conf = json.load(open('config.json'))
  else:
    conf = dict()
  conf['download'] = float(input('Download (mbps): '))
  conf['upload'] = float(input('Upload (mbps): '))
  if 'y' in input('Enable email notifications? (y/n): ').lower():
    conf['recipient'] = input('Email:')
  return conf


def logger(down, up):
  if os.path.exists('log.json'):
    with open('log.json','r') as f:
      log = json.load(f)
  else:
    log = {}
  now = strftime("%Y-%m-%d:%H", gmtime())
  log[now] = (down, up)
  with open('log.json','w') as f:
    json.dump(log, f, indent=2)


def sendEmail(body, img=None):
  with open('config.json','r') as f:
    conf = json.load(f)
  if 'recipient' not in conf:
    print("Email functionality has not been configured. If you'd like to enable this functionality, run the program with the '--config' option.")
    sys.exit()
  addr = 'network.monitor337@gmail.com'
  msg = EmailMessage()
  msg['From'] = addr
  msg['To'] = conf['recipient']
  msg['Subject'] = 'Network Monitor Info'
  msg.set_content(body)
  if img:
    with open(img, 'rb') as f:
      img_data = f.read()
    msg.add_attachment(img_data, maintype='image', subtype='png')
  try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
  except:
    print("Something went wrong")
  # make connection secure
  server.starttls()
  server.login(addr,'cst337project')
  server.send_message(msg)
  server.quit()


def report(target):
  with open('log.json','r') as f:
    log = json.load(f)
  if len(log.keys()) > 720:
    keys = log.keys()[-720:]
  else: 
    keys = log.keys()
  down, up = 0, 0
  for i in keys:
    if float(log[i][0]) < target['download']:
      down += 1
    if float(log[i][1]) < target['upload']:
      up += 1
  down_perc = round(down/len(keys)*100,2)
  up_perc = round(up/len(keys)*100,2)
  return str(down_perc)+"% of the recordings fell below your target download speeds. \n"+str(up_perc)+"% of the recordings fell below your target upload speeds.\n"


def create_graph():
  with open('log.json','r') as f:
    log = json.load(f)
  if len(log.keys()) >=720:
    keys = log.keys()[-720:]
  else: 
    keys = log.keys()
  download = [int(log[i][0]) for i in log.keys()]
  upload = [int(log[i][1]) for i in log.keys()]
  x = [i for i in range(len(log.keys()))]
  # size = (8, 4)
  if len(log.keys()) > 100: 
    # size = (len(log.keys())//20, max(download)//25)
    ax = plt.axes()
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
  # plt.figure(figsize=size)
  plt.figure()
  x = np.arange(0.0, len(keys), 1)
  plt.plot(np.arange(0.0, len(keys), 1), download, label="Download")
  plt.plot(np.arange(0.0, len(keys), 1), upload, label="Upload")
  plt.xticks(x, log.keys(), rotation='65')
  plt.xlim(0, len(log.keys()))
  plt.ylim(0, max(download)+10)
  plt.title('Network Data Speeds')
  plt.xlabel('Time')
  plt.ylabel('Speed (mbps)')
  plt.legend(loc='upper right')
  plt.grid(True)
  plt.gcf().subplots_adjust(bottom=0.15)
  plt.tight_layout()
  plt.savefig(str(strftime("%Y-%m-%d_%H:%M", gmtime()))+'.png')
  return plt


if __name__ == "__main__":
  main()
