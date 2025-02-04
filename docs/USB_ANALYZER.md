# USB traffic analyzer tutorial

## Introduction

As an alternative of using Wireshark, you might try to use the project's USB traffic analyzer instead first.

It uses the tshark Wireshark's CLI tool to do what you'd do with wireshark, in an easier way.

## Requisites

1. The SteelSeries GG software installed (on a Windows host, or a Windows VM with attached SteelSeries USB device)
2. Wireshark installed on Windows, **with usbpcap drivers**. Don't forget to reboot after install, as suggested by the software installer!
3. The USB analyzer found [here](./usb_helper/). In this tutorial I'll reference to the one-file binary file. In order to run it via python, see the following sub-chapter.

### USB analyzer

If you want to run it from the sources, you need to install the dependencies first via pipenv, then run, it like this:

```cmd
cd .\usb_helper
pipenv install
pipenv run python .\main.py
```

You can also build your own executable, instead of downloading it from the releases page, like this:

```cmd
cd .\usb_helper
pipenv install -d
pipenv run pyinstaller
```

You will then find the `arctis_usb_analyzer.exe` file in the `usb_helper\dist` folder.

## Step 1: download the analyzer or the source (to run it via python natively)

You can find the latest analyzer package in the releases page. The binary is the `pyinstaller` packaged python script.

You can still download the source code and execute it as described in the previous chapter.

## Step 2: run the analyzer

Simply run the analyzer and follow the instructions. In the end it will produce a markdown file you'll be able to read, or submit in an issue ticket to get help / ask for implementation.

Note: the script will ask for administrative privileges due to the need to access the low-level USB interfaces. If you don't trust it, read the code and run from the sources!

## Step 3: implement the device handler, or submit an issue

With the information gathered, you can write your own device manager. Take a look on [ArctisNovaProWirelessDeviceManager](../arctis_manager/devices/device_arctis_nova_pro_wireless.py) to get an idea on how to manage the device status.

Each device might differ, for example the Arctis Nova Pro Wireless handles the volume by itself, while the Arctis 7 needs software volume management.

## Final words

The script is still not perfect nor has all the information you need to know to jump-start. For example you still need to figure out the device's product id, you need to figure out what's the command to get the status (it might lay in the initialization sequence) and how to parse its response.

For advances sniffing, [Wireshark](WIRESHARK.md) is still the best tool, as this is solely a "managed" wireshark helper, which might ignore important data.

The tool, if it detects the device identifier, will print a suggested filter to use to track the device's packets only, which allows you to skip the Wireshark tutorial's steps up to "**Step 2: watch the packets**".
