import sys, os, re, glob, argparse, subprocess, json, smtplib
import pylab as plt
from time import gmtime, strftime
from email.message import EmailMessage


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--config', action="store_true", help='set the target download and upload speeds (mbps)')
  parser.add_argument('-q', '--quiet', action="store_true", help='logs network speed without output')
  parser.add_argument('-g', '--graph', action="store_true", help='displays a graph of data speeds for the last 30 days')
  parser.add_argument('-r', '--report', action="store_true", help='sends an email with a report of your network data speeds for the last 30 days')
  args = parser.parse_args()
  network_status = True
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
    if not network_status:
      sendEmail('Your network is back online')
    network_status = True
  except:
    current = (0,0)
    network_status = False
    sendEmail('Your network appears to be offline')
    print('Your network appears to be offline')

  # Log current data speeds
  log(current[0], current[1])
  status = ['download','upload']
  for j,i in enumerate(status):
    print(str(i[0].capitalize())+': '+str(current[j])+' mbps')

  if args.graph:
    plt = create_graph()
    plt.show()
  
  if args.report:
    create_graph()
    sendEmail(f"{report(target)} \nThe following graph shows your network speed for the month", sorted([file for file in glob.glob("*.png")])[0])
    sys.exit()


def test_speed():
  speed = subprocess.check_output(['python', 'speedtest.py', '--simple']).decode()
  return tuple([float(re.findall('\d+\.\d+', i)[0]) for i in speed.splitlines()[1:]])

def config():
  if os.path.exists('config.yml'):
    conf = json.load(open('config.json'))
  else:
    conf = dict()
  conf['download'] = float(input('Download (mbps): '))
  conf['upload'] = float(input('Upload (mbps): '))
  if 'y' in input('Enable email notifications? (y/n): ').lower():
    conf['recipient'] = input('Email:')
  return conf


def log(down, up):
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
    with open(img, 'rb') as fp:
      img_data = fp.read()
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
  return f'{down_perc}% of the recordings fell below your target download speeds. \n {up_perc}% of the recordings fell below your target upload speeds.\n'

def create_graph():
  with open('log.json','r') as f:
    log = json.load(f)
  if len(log.keys()) >=720:
    keys = log.keys()[-720:]
  else: 
    keys = log.keys()
  range = plt.arange(0.0, len(keys), 1)
  download, upload = [], []
  for i in log.keys():
    download.append(int(log[i][0]))
    upload.append(int(log[i][1]))
  x = [i for i in log.keys()]
  plt.plot(range, download, label="Download")
  plt.plot(range, upload, label="Upload")
  plt.ylim(0, max(download)+5)
  plt.xlabel('Time')
  plt.ylabel('Speed')
  plt.legend(loc='upper right')
  plt.title('Network Data Speeds')
  plt.grid(True)
  plt.savefig(str(strftime("%Y-%m-%d_%H:%M", gmtime()))+'.png')
  return plt


if __name__ == "__main__":
  main()
