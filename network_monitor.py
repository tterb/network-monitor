import sys, os, argparse, json, pyspeedtest, random
from time import gmtime, strftime
from twilio.rest import Client
from subprocess import check_output
import pylab as plt


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

  # Get current data speeds
  try:
    current = test_speed()
    # if not network_status:
    #   sendSMS('Your network is back online')
    network_status = True
  except:
    current = (0,0)
    network_status = False
    # sendSMS('Your network appears to be offline')
    print('Your network appears to be offline')

  # Log current data speeds
  log(current[0], current[1])

  if not args.quiet:
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
    sys.exit()


def test_speed():
  speed = pyspeedtest.SpeedTest()
  return (float("%0.2f"%(speed.download()/1000000)), float("%0.2f"%(speed.upload()/1000000)))


def config():
  download = float(input('Download (mbps): '))
  upload = float(input('Upload (mbps): '))
  return {'download': download, 'upload': upload}


def log(down, up):
  # print(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))
  with open('log.json','r') as f:
    log = json.load(f)
  while len(log.keys()) >= 720:
    del log[log.keys()[0]]
  now = strftime("%Y-%m-%d_%H:%M", gmtime())
  log[now] = [down, up]
  with open('log.json','w') as f:
    json.dump(log, f, indent=2)


# def sendSMS(msg):
#   # Create client with Twilio Account SID and Auth Token
#   # client = Client('ACf0fabfa03ef65b8fa267366f0ee496c1', 'a2294ea36a3029fbac5adfbd6b902456')  # Test
#   client = Client('ACf46cbb5d26b14a14ac8bb3b63954dc4d', '075c1400a0af529b0eb21ded9dbd78f7') # Not test
#   # message = client.messages.create(body=msg, to='+12244360022', from_='+15005550006')
#   message = client.messages.create(body=msg, to='+18476361145', from_='+12244360022')
#   print(message.sid)


def create_graph():
  with open('log.json','r') as f:
    log = json.load(f)
  # range = arange(0.0, 720.0, 1)
  range = plt.arange(0.0, float(len(log.keys())), 1)
  down, up = [], []
  for i in log.keys():
    down.append(int(log[i][0]))
    up.append(int(log[i][1]))
  plt.plot(range, down, label="Download")
  plt.plot(range, up, label="Upload")
  # target = plt.plot(range, [85]*len(log.keys()), label="D/L Target")
  # plt.setp(target, color='r', ls='--', linewidth=0.5)
  plt.xlim(0, len(log.keys()))
  plt.ylim(0, max(down)+5)
  plt.xlabel('Time')
  plt.ylabel('Speed')
  plt.legend(loc='upper left')
  plt.title('Network Data Speeds')
  # plt.gcf().autofmt_xdate()
  # plt.figtext(0.075, 0.04, 'Max Download: '+str(max(down)), horizontalalignment='left')
  # plt.figtext(0.075, 0.01, 'Max Upload: '+str(max(up)), horizontalalignment='left')
  plt.grid(True)
  plt.savefig(str(strftime("%Y-%m-%d_%H:%M", gmtime()))+'.png')
  plt.show()


if __name__ == "__main__":
  main()
