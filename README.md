# esp8266-mqtt-home-automation-nodes
Nodes for the ESP8266 microcontroller in micropython

## Deploy

First if needed, copy the micropython-libs needed, if not in your firmware, together with drivers folder and project folder:
```
./tools.py go weather-node drivers lib
```

Next time it is enough to deploy source for project folder
```
./tools.py go weather-node
```

## Flash the chip with micropython firmware
Make sure you have a build tree with pre-built firmware image and the paths in tools.py configured. You also need 'esptools' installed with python3 support.

Then run:
```
./tools.py reflash
```

You can also install a downloaded prebuilt binary for FW.
