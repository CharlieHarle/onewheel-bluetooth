import logging
import paho.mqtt.client as mqtt
from readdata import get_json_data

from config import BROKER_IP, CLIENT_NAME, CLIENT_PASSWORD, ONEWHEEL_MAC

logging.basicConfig()
logger = logging.getLogger('_onewheel_stats_')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('output.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


TOPIC = 'home/onewheel'

logger.info('Starting log sequence to topic: {}'.format(TOPIC))

json_data = get_json_data(logger)

client = mqtt.Client()
client.enable_logger()
client.username_pw_set(username=CLIENT_NAME, password=CLIENT_PASSWORD)
client.connect(BROKER_IP)

if json_data:
  client.publish(TOPIC, json_data)
  logger.info('Successfully sent data to Home Assistant: {}'.format(json_data))
else:
  logger.info('Logged nothing to HA cos ble sucks')
