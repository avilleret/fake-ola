# fake-ola
python script that mimic OLA server to drive APA102 LED with a Raspberry Pi

APA102 should be plugged directly to Raspberry Pi MOSI, CLK and GND.
And you should use a seperate power supply for the LEDs (the 5V onboard regulartor of the Pi coul only drive very few pixels before burning).

`fake-ola.sh` is intended to be symlink into `/etc/init.d/`, then use the common `sudo update-rc.d default fake-ola` to add it to services to start with system.

By default `fake-ola.py` log is in `/tmp/fake-ola.log`.
