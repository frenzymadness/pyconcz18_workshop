# Prerequisites

To save some time and don't waste it waiting for download a bunch of data on almost thirty computers, please prepare some software in advance.

## Vagrant (+ VirtualBox)

Vagrant is an awesome tool to manage various virtualization platforms for you and it is able to provision whole virtual machine from settings in one file. Vagrantfile for our workshop is available in this repository.

If you are new to Vagrant, you'll also need some virtualization backend. To keep it simple, download and install Virtualbox. If you are using some other like libvirt, keep it.

* Vagrant: https://www.vagrantup.com/downloads.html
* Virtualbox: https://www.virtualbox.org/wiki/Downloads

## Python

We are on Pycon, right? :) I suppose that you have Python already installed but just to make sure.

We'll need to install one package from PyPI so we need to have Python 3 installed.

* Python: https://www.python.org/downloads/

# Introduction

## Who I am

Lumír Balhar, Python software engineer, member of Python maintenance team in Red Hat, Pyvo meetup org, PyLadies main coach.

## What we'll do today

We are gonna build simple Python-based home automation system with MQTT communication between a wireless temperature sensor and Home Assistant.

# Hardware

I'll borrow you all the stuff you'll need. If you want, you can buy the whole set at the end of the workshop.

## Breadboard, wires, microUSB

We are gonna use microUSB cable to power NodeMCU board and breadboard + wires to connect temperature sensor to NodeMCU.

## DS18B20 temperature sensor

Very cheap and well-known temperature sensor from Maxim integrated. It uses OneWire bus for communications which allows you to connect multiple sensors to one bus.

## NodeMCU

NodeMCU is a smart board with ESP8266 WiFi chip which has so much computing power that it can run Python (MicroPython).

# Software

## Drivers

If you are on Windows, you'll probably need to install drivers to be able to communicate with NodeMCU.

Connect NodeMcu with your computer using microUSB cable. Be careful! Don't let the silver pack touch the NodeMCU when it's connected. It can short pins and destroy the board.

* On Linux, run `dmesg | tail`. You should see that a new device is registered under name ttyUSB0 or similar.
* On Windows, open device manager and check whether the device was recognized or not. If not, install a proper driver from `drivers` directory. When the device will be recognized successfully, remember the COM port name.

## Picocom/Putty

We need some software to connect to the NodeMCU and to check that everything works. You'll need it also for checking the status of measuring later.

* On Linux, install package `picocom` which is available in Fedora, Ubuntu and others. If you like other software for serial communication, feel free to use it.
* On Windows, download Putty from [this site](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html). You can install Putty system-wide or use standalone executable.

## MicroPython

Special port of Python for small IoT devices. It's different than CPython because it contains modules for communication with external devices and doesn't contain some parts of the standard library, help etc. to be small enough for IoT devices.

All NodeMCU already contains the latest MicroPython.

Now is time to connect to NodeMCU and play with MicroPython.

* On Linux, run `picocom -b 115200 --flow n /dev/ttyUSB0` in command line. Don't forget to change the name of the device to proper one.
    * If you get "no such file or directory error" you probably did a typo in the name of the device. Check it and also check the output of `dmesg | tail` once again.
    * If you get a permission error, you'll need to become a member of `dialout` group. Run `sudo usermod -a -G dialout $(whoami)` and then `su - $(whoami)` to relogin. Output of `groups` command should contain dialout in the list of groups now.
* On Windows, run Putty, switch Connection type to Serial, type your COM port into Serial line. Then switch to Serial in the left menu and set Speed to 115200 and Flow control to None. Now click on Open button.

When connected, try to hit Enter or restart the NodeMCU by the RST button near the microUSB connector. You should see `>>>` - the Python prompt!

Lets play with it for a little bit until we solve all connection issues and try to find some differences between standard CPython implementation and MicroPython.

Homepage: http://micropython.org/

## Ampy

Ampy (Adafruit MicroPython tool) is a handy piece of software which can help us to manage files stored on NodeMCU and also run Python scripts directly from a computer.

Ampy is available as a package on PyPI so it can be simply installed by `pip install adafruit-ampy`. Feel free to install it system-wide or into virtual environmet if you know how to do it. There is also ampy package available in Fedora packages repositories.

Homepage: https://github.com/adafruit/ampy

## Mosquitto

Mosquitto is a simple MQTT broker service which means that it will stay in the middle between message publishers (sensors) and subscribers (home assistant) and it'll take care of receiving and delivering of all measured values.

Mosquitto is already installed and ready in VM. Installation is pretty simple. Take a look into Vagrantfile to know how to do it next time.

Homepage: https://mosquitto.org/

## Home Assistant

Home Assistant is a heart of our home automation platform and we'll spend most of our time configuring it to subscribe to our MQTT topics, show measured data in graph and send some notification for configured events.

Home Assistant is also prepared in virtual machine.

https://www.home-assistant.io/

# Preparing sensor

## Hardware

Before any manipulation, make sure that the NodeMCU is disconnected from a power source (computer)!

To connect the sensor to the NodeMCU use this schema:

![DS18B20 wiring](./images/DS18B20 wiring.png)

## Source code

Source code for your first sensor is ready in `scripts` folder and it is called `DS18B20.py`.

The script has to be modified before we can upload it. Open it in your favorite editor and change global variables at the top of the file. You have to change at least IP address of MQTT broker which is actual IP address of your computer.

To upload this code to NodeMCU we'll use ampy.

```
ampy -p /dev/ttyUSB0 put DS18B20.py main.py
```

The first name is the name of script on your computer and the second name is the name of the script on NodeMCU. When the name of the script on NodeMCU is `main.py` it is executed automatically after every restart.

## Testing

To test that it actually works, we can subscribe to the topic on MQTT broker. To do that, run this command in the virtual machine. Don't forget to change topic name.

```
mosquitto_sub -h 127.0.0.1 -d -t temp
```

If it doesn't work, connect to the device directly using picocom or Putty, restart it and see the output in the terminal.

# Configuring HA

HA frontend is already available at http://127.0.0.1:8123

Try it!

## Basic configuration

First, go to the folder `/home/vagrant/.homeassistant/` where all configuration files are located. Now we make some changes to the default configuration.

* Comment out `introduction` which will remove links from main page.
* Comment out `discovery` which will turn off automatic discovery.
* Comment out `cloud` which will disable cloud integration.

## Weather from the Internet

Yr platorm provides more than just weather symbol so for the start, let's configure this sensor to gain more data. Place this configuration directly under the `platform: yr`.

```
monitored_conditions:
    - temperature
    - symbol
    - windSpeed
    - windDirection
    - humidity
    - cloudiness
```

## MQTT broker

Let's set up a connection to MQTT broker, which allows us to read measured values from MQTT and show them in HA.

Add these lines somewhere to the configuration file:

```
mqtt:
    broker: 127.0.0.1
    client_id: HA
```

Let's check the configuration and restart the core to load it.

## New sensor

MQTT integration is ready for the first MQTT based sensor. Let's configure it.

Add these lines somewhere to the file. Don't forget to change the topic is you changed it before in the script.

```
sensor pycon_temp:
  name: "Pycon temp"
  platform: mqtt
  state_topic: "temp"
  qos: 1
  expire_after: 600
  force_update: true
  unit_of_measurement: "°C"
```

## Better UI

Let's customize the boring UI a little bit.

Groups of devices are also automatically converted to groups in UI so let's create two groups:

```
group:
  Internet:
    entities:
      - sun.sun
      - sensor.yr_symbol
      - sensor.yr_cloudiness
      - sensor.yr_humidity
      - sensor.yr_temperature
      - sensor.yr_wind_direction
      - sensor.yr_wind_speed
  My sensors:
    entities:
      - sensor.pycon_temp
```

## Graphs

See measured temperatures is great. See the history of values is better. Let's create a graph!

```
history_graph:
  pycon_temp:
    name: "PyconCZ temp graph"
    entities:
     - sensor.pycon_temp
     - sensor.yr_temperature
    hours_to_show: 12
    refresh: 60
```

## Notifications

There are a lot of platforms for notifications: https://www.home-assistant.io/components/notify/

We'll try to implement Slack because we have Slack for all Pycon attendees but you can try whatever you want if you find a suitable plugin for service you use.

Let's enable Slack plugin and configure it:

```
notify:
  - name: slack
    platform: slack
    api_key: <API KEY HERE>
    default_channel: '#ha-workshop'
    username: 'Test_user'
```

Now you can test it. In the left pane on HA frontend click on the bottom left icon "Services". In this page, you can test all provided services. Let's chose notify.slack and paste following JSON to "Service Data" input:

```
{"message":"your message"}
```

## Automation

The workshop is called "Home automation", right? Let's create one.

You can create automations in config files and at this time it makes sense to split configuration into multiple files. It's also possible to do it in web interface so let's try it.

Open Configuration > Automation and click on "Plus" symbol in the right bottom corner. You can choose the name of automation, a trigger which will cause execution of an automation, conditions to evaluate and action to do at the end. You can have multiple triggers, conditions and also multiple actions.

Add a numeric state trigger which will be executed when the temperature measured by your sensor will be higher than 25 degrees. Let conditions empty and add an action which will call service notify.slack with some general message (in JSON format).

HA supports Jinja templates so you can add sensor state to the message with `{{ states.sensor.pycon_temp.state }}`.

# Conclusion

Hope you liked our workshop. Now you can buy the whole set which contains:

* NodeMCU smart board
* breadboard
* wires
* microUSB cable
* DS18B20 temperature sensor

Price is 150 CZK or 6 Euro. It's basically the same price you can buy this set on Aliexpress or Ebay for. Additional value is that you don't have to wait :)

# Next steps

* You can add as many sensors as you want based on different hardware or create own hardware.
* Add more groups and views to make your UI uniq and clear.
* You can make some hardware which will listen to commands from HA (MQTT).
* You can fully automate your home ... impossible is nothing.
