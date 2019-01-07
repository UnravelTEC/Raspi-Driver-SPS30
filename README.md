# Raspi-Driver-SPS30
Software to read out [Sensirion SPS30](https://www.sensirion.com/en/environmental-sensors/particulate-matter-sensors-pm25/) PM sensor values over I2C on Raspberry Pi.

This software is licenced under GPLv3 by [UnravelTEC OG](https://unraveltec.com) (https://unraveltec.com), 2018.

## Prerequsites 

Maximum I2C speed for SPS30 is 100kHz (Default on Raspbian).

Recommended maximum I2C cable length 20cm.

Sensor needs 5V, on I2C bus 3.3V is fine. Seems to work without external pull-ups on Raspberry Pi 3B+.

### Python 

Install the following python-libraries:

```
aptitude install python-crcmod
```

### Pigpiod

As the SPS30 needs complex i2c-commands, the Linux standard i2c-dev doesn't work. A working alternative is pigpiod.

```
aptitude install pigpio python-pigpio
```

Atm, IPv6 doesn't work on Raspbian correctly with pigpiod, so:

```
sed -i "s|^ExecStart=.*|ExecStart=/usr/bin/pigpiod -l -n 127.0.0.1|" /lib/systemd/system/pigpiod.service
systemctl restart pigpiod
# Test (should return an int)
pigs hwver
```

## Run program

```
python sps30.py
```

## Installation

To install it as a background service run ./install.sh (install dependencies, e.g. via apt, first).

This service writes a file - suited for scraping by prometheus - (onto ramdisk on /run/sps30) and updates it every second.
