import logging
from argparse import ArgumentParser
from binascii import hexlify
from hashlib import md5
from time import sleep

from pygatt import BLEAddressType, GATTToolBackend, exceptions
from config import ONEWHEEL_MAC
from onewheel import UUIDs

import json


adapter = GATTToolBackend()
ADDRESS_TYPE = BLEAddressType.public
key_input = bytearray()


def get_json_data(logger):
    """ Build json blob to send to HA via paho MQTT"""
    data = {}
    adapter.start()
    try:
        device = adapter.connect(ONEWHEEL_MAC, address_type=ADDRESS_TYPE)
    except exceptions.NotificationTimeout:
        logger.warning('Unable connect to device. Is it busy?')
    try:
        unlock_gatt_sequence(device)
    except (exceptions.NotificationTimeout, exceptions.NotConnectedError):
        logger.warning('Unable to unlock gatt sequence')
        pass
    try:
        print("Reading values...")
        battery_remaining_value = device.char_read(UUIDs.BatteryRemaining)
        data['battery_remaining'] = get_human_friendly(battery_remaining_value)

        lifetime_odometer_value = device.char_read(UUIDs.LifetimeOdometer)
        data['lifetime_odometer'] = get_human_friendly(lifetime_odometer_value)

        trip_odometer_value = device.char_read(UUIDs.Odometer)
        data['trip_odometer'] = get_human_friendly(trip_odometer_value)

        pitch_value = device.char_read(UUIDs.TiltAnglePitch)
        pitch_raw = get_human_friendly(pitch_value)
        data['pitch'] = round((pitch_raw / 10) - 360, 1)

        roll_value = device.char_read(UUIDs.TiltAngleRoll)
        roll_raw = get_human_friendly(roll_value)
        data['roll'] = round(180 - (roll_raw / 10), 1)

        yaw_value = device.char_read(UUIDs.TiltAngleYaw)
        yaw_raw = get_human_friendly(yaw_value)
        data['yaw'] = round(yaw_raw / 10, 1)
    except exceptions.NotificationTimeout:
        logger.warning('Unable to read values')
        pass
    finally:
        device.disconnect()
        adapter.stop()

    logger.info('Successfully received data from Onewheel: {}'.format(data))
    return json.dumps(data)


def get_human_friendly(value):
    """ Return base 10 integer from hex value"""
    return int(hexlify(value), 16)


def handle_key_response(_, data):
    """ Append all key responses to the global key """
    global key_input
    key_input += data


def unlock_gatt_sequence(device):
    """ Unlock lasts about 25 seconds, if we are doing more than one read, we will need to call this more """
    print("Requesting encryption key...")
    device.subscribe(UUIDs.UartSerialRead, callback=handle_key_response, wait_for_response=False)
    version = device.char_read(UUIDs.FirmwareRevision)
    device.char_write(UUIDs.FirmwareRevision, version, True)
    wait_for_key_response()
    key_output = create_response_key_output()
    device.char_write(UUIDs.UartSerialWrite, key_output)
    device.unsubscribe(UUIDs.UartSerialRead, wait_for_response=False)
    sleep(0.5)  # wait a moment for unlock


def create_response_key_output():
    """ Build the response key we will send to the board to unlock access to characteristic values """
    array_to_md5 = key_input[3:19] + bytearray.fromhex("D9 25 5F 0F 23 35 4E 19 BA 73 9C CD C4 A9 17 65")
    hashed = md5(array_to_md5)
    key_output = bytearray.fromhex("43 52 58")
    key_output += hashed.digest()
    key_output += calculate_check_byte(key_output)
    return key_output


def wait_for_key_response():
    """ Wait for full key from notifications with 30 second timeout """
    timeout = 30.0
    while len(key_input) < 20 and timeout > 0:
        print("Waiting for encryption key...")
        sleep(0.25)
        timeout -= 0.25
    if timeout == 0:
        print("Error: timeout reached waiting for encryption key response.")
        quit(2)


def calculate_check_byte(key_output):
    """ Calculate the final check byte for the response key """
    check_byte = 0x00
    i = 0
    arr_len = len(key_output)
    while i < arr_len:
        check_byte = key_output[i] ^ check_byte
        i += 1
    return bytes([check_byte])
