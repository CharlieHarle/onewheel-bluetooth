# onewheel-bluetooth
A python bluetooth data reader for the Onewheel (supporting Gemini firmware).
This is meant to be a quick and dirty example of how to connect and obtain data from the board and pass to Home Assistant via MQTT

## Usage

1) Create python file called `config.py` in the base dir and enter your any variables referenced in the code from there for example:

```python
BROKER_IP = "192.168.1.55"
CLIENT_NAME = "bilbo"
CLIENT_PASSWORD = "shhitsasecret"
ONEWHEEL_MAC = "00:00:00:00:00:00"
```

2) Run `mqtt.py` with cron ([see documentation](https://www.raspberrypi.org/documentation/linux/usage/cron.md)) on your BLE compatible pi (I used a Zero W)

You should get output like the following:

```
Requesting encryption key...
Waiting for encryption key...
Reading values...
Sending json blob: {"battery_remaining": 100, "lifetime_odometer": 132, "trip_odometer": 0, "pitch": -91.9, "roll": -13.3, "yaw": 270.6}
```

Now go to your Home Assistant add some sensors to `sensor.yaml`

```yaml
- platform: mqtt
  state_topic: "home/onewheel"
  name: onewheel_battery_remaining
  icon: mdi:battery-charging
  value_template: "{{ value_json.battery_remaining }}"
  unit_of_measurement: '%'
- platform: mqtt
  state_topic: "home/onewheel"
  name: onewheel_lifetime_odometer
  icon: mdi:highway
  value_template: "{{ value_json.lifetime_odometer }}"
  unit_of_measurement: 'mi'
- platform: mqtt
  state_topic: "home/onewheel"
  name: onewheel_trip_odometer
  icon: mdi:bike
  value_template: "{{ value_json.trip_odometer }}"
  unit_of_measurement: 'mi'
- platform: mqtt
  state_topic: "home/onewheel"
  name: onewheel_pitch
  icon: mdi:arrow-up-down-bold
  value_template: "{{ value_json.pitch }}"
  unit_of_measurement: '°'
- platform: mqtt
  state_topic: "home/onewheel"
  name: onewheel_roll
  icon: mdi:cached
  value_template: "{{ value_json.roll }}"
  unit_of_measurement: '°'
- platform: mqtt
  state_topic: "home/onewheel"
  name: onewheel_yaw
  icon: mdi:arrow-left-right-bold
  value_template: "{{ value_json.yaw }}"
  unit_of_measurement: '°'
```

### Credits
ariudo/onewheel-bluetooth

Thanks to [@kariudo](https://github.com/kariudo) for making a simple python script to handle all the nasty bluetooth handshaking on the Onewheel.
