import sys, os, re, argparse, subprocess, json, smtplib
import pylab as plt
from time import gmtime, strftime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--config', action="store_true", help='set the target download and upload speeds (mbps)')
  parser.add_argument('-q', '--quiet', action="store_true", help='logs network speed without output')
  parser.add_argument('-g', '--graph', action="store_true", help='displays a graph of data speeds for the last 30 days')
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

  status = []
  if current[0] < target['download']:
    status.append(('download','below'))
  else:
    status.append(('download','above'))
  if current[1] < target['upload']:
    status.append(('upload','below'))
  else:
    status.append(('upload','above'))

  for j,i in enumerate(status):
    print(str(i[0].capitalize())+': ', end='')
    if 'below' in i:
      print(str(current[j])+' mbps')
    else:
      print(str(current[j])+' mbps')

  if args.graph:
    create_graph()
    sendEmail(f'Download: '+str(current[0])+" mbps \nUpload: "+str(current[1])+' mbps')


def test_speed():
  ip = get('https://api.ipify.org').text
  speed = subprocess.check_output(['python', 'speedtest.py', '--simple']).decode()
  return tuple([float(re.findall('\d+\.\d+', i)[0]) for i in speed.splitlines()[1:]])


def config():
  conf['download'] = float(input('Download (mbps): '))
  conf['upload'] = float(input('Upload (mbps): '))
  if 'y' in input('Enable email notifications? (y/n): ').lower():
    conf['email'] = input('Email address: ')
    conf['password'] = input('password: ')
  return conf


def log(down, up):
  if os.path.exists('log.json'):
    with open('log.json','r') as f:
      log = json.load(f)
  else:
    log = {}
  now = strftime("%Y-%m-%d:%H", gmtime())
  # now = str(dt.datetime.now()).split('.')[0]
  log[now] = (down, up)
  with open('log.json','w') as f:
    json.dump(log, f, indent=2)


def sendEmail(body):
  with open('config.json','r') as f:
    config = json.load(f)
  if 'email' not in config:
    print("Email functionality has not been configured. If you'd like to enable this functionality, run the program with the '--config' option.")
    sys.exit()
  addr = config['email']
  msg = MIMEText(body)
  msg['From'] = addr
  msg['To'] = addr
  msg['Subject'] = 'Network Monitor Info'
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  server.login(addr, config['password'])
  server.send_message(msg)
  server.quit()


def create_graph():
  with open('log.json','r') as f:
    log = json.load(f)
  # range = arange(0.0, 720.0, 1)
  range = plt.arange(0.0, int(len(log.keys())), 1)
  download, upload = [], []
  for i in log.keys():
    download.append(int(log[i][0]))
    upload.append(int(log[i][1]))
  x = [i for i in log.keys()]
  # y = [str(log[i][0]) for i in log.keys()]
  # plt.plot(x,download,label="DL")
  plt.plot(range, download, label="Download")
  plt.plot(range, upload, label="Upload")
  plt.gcf().autofmt_xdate()
  # target = plt.plot(range, [85]*len(log.keys()), label="D/L Target")
  # plt.setp(target, color='r', ls='--', linewidth=0.5)
  # plt.xlim(0, len(log.keys()))
  plt.ylim(0, max(download)+5)
  plt.xlabel('Time')
  plt.ylabel('Speed')
  plt.legend(loc='upper right')
  plt.title('Network Data Speeds')
  # plt.gcf().autofmt_xdate()
  # plt.figtext(0.075, 0.04, 'Max Download: '+str(max(down)), horizontalalignment='left')
  # plt.figtext(0.075, 0.01, 'Max Upload: '+str(max(up)), horizontalalignment='left')
  plt.grid(True)
  plt.savefig(str(strftime("%Y-%m-%d_%H:%M", gmtime()))+'.png')
  plt.show()


if __name__ == "__main__":
  main()
