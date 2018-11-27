import paho.mqtt.client as mqtt
from readdata import get_json_data

from config import BROKER_IP, CLIENT_NAME, CLIENT_PASSWORD, ONEWHEEL_MAC

TOPIC = 'home/onewheel'

json_data = get_json_data()

client = mqtt.Client()
client.enable_logger()
client.username_pw_set(username=CLIENT_NAME, password=CLIENT_PASSWORD)
client.connect(BROKER_IP)

print("Sending json blob: {}".format(json_data))

client.publish(TOPIC, json_data)
