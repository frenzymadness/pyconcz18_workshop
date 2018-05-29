import network
from time import sleep
import machine
import onewire
from ds18x20 import DS18X20
from umqtt.simple import MQTTClient

# WiFi
SSID = "frenzy-wifi-home"
PASSWORD = "password"
# Sensor
PIN = 2
# MQTT
SERVER_IP = "10.0.0.108"
CLIENT = 'test_sensor'
TOPIC = b'temp'


def connect_to_wifi(ssid, password):
    wifi = network.WLAN(network.STA_IF)

    if wifi.isconnected():
        print("Already connected to Wifi")
        return

    wifi.active(True)
    wifi.connect(ssid, password)

    print('Connecting .', end=' ')

    while not wifi.isconnected():
        sleep(1)
        print('.', end=' ')

    print("Connection successful")
    print(wifi.ifconfig())


def pub_message(server, topic, message):
    c = MQTTClient(CLIENT, server)
    c.connect()
    sleep(1)
    c.publish(topic, message, qos=1)
    sleep(1)
    c.disconnect()


def main():
    connect_to_wifi(SSID, PASSWORD)

    print('Initial delay ...')
    sleep(5)

    pin = machine.Pin(PIN)
    ow = DS18X20(onewire.OneWire(pin))

    sensors = ow.scan()

    if not sensors:
        print('Cannot find any OneWire sensor')
        return

    while True:
        for sensor in sensors:
            # Measuring
            try:
                ow.convert_temp()
                sleep(1)
                temp = ow.read_temp(sensor)
            except Exception as e:
                print('ERROR while reading from OneWire')
                print(e)

            # Sending to MQTT
            try:
                pub_message(SERVER_IP,
                            TOPIC,
                            b'{}'.format(temp))
            except Exception as e:
                print('ERROR while publishing message to MQTT')
                print(e)

        sleep(60)


if __name__ == '__main__':
    main()
