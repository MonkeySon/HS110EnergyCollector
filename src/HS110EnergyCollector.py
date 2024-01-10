import sys
import json
import traceback
import time
import socket

from HS110 import HS110
from HS110EnergyPoint import HS110EnergyPoint
import MailifierUtil
import InfluxDBConnector

CONFIG_FILE_NAME = 'config.json'

if len(sys.argv) == 2:
    CONFIG_FILE_NAME = sys.argv[1]
elif len(sys.argv) > 2:
    print(f'Usage: {sys.argv[0]} [ CONFIG_FILE ]')
    exit(1)

print(f'Using config file: {CONFIG_FILE_NAME}')

try:
    with open(CONFIG_FILE_NAME, encoding='UTF-8') as config_file:
        cfg = json.load(config_file)
except Exception as e:
    print('Exception while opening config file:', e)
    print(traceback.format_exc())

hs110 = HS110(cfg['hs110_ip'])
interval = cfg['interval_sec']
influxDBCfg = cfg['influxDB']

print('Starting HS110 Energy Collector ...')

print('Connecting ...')
try:
    hs110.connect()
except Exception as e:
    print('Exception during initial connection:', e)
    print(traceback.format_exc())
    MailifierUtil.mailify_exception('Exception during initial connection')
    exit(1)
print('Connected!')

def handle_reconnect(retries=10):
    for _ in range(retries):
        try:
            hs110.connect()
            print('Reconnected!')
            return
        except socket.timeout:
            print('Reconnect timed out, retrying ...')
        except Exception as e:
            print('Exception during reconnect:', e)
            print(traceback.format_exc())
            MailifierUtil.mailify_exception('Exception during reconnect')
            exit(1)
    print(f'Could not reconnect after {retries} times!')
    MailifierUtil.mailify('Reconnect error', f'Could not reconnect after {retries} times!')
    exit(1)

print('Starting to collect energy data ...')
while True:
    try:
        energy_json = hs110.get_energy()
        ep = HS110EnergyPoint(energy_json)
        InfluxDBConnector.write_point(influxDBCfg, ep)
        time.sleep(interval)
    except socket.timeout:
        print('Socket timed out, reconnecting ...')
        handle_reconnect()
    except Exception as e:
        print('Exception during execution:', e)
        print(traceback.format_exc())
        MailifierUtil.mailify_exception('Exception during execution')
        exit(1)