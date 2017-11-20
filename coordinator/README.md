# Coordinator Setup

The Raspberry Pi must be configured prior to any installation of hardware or software. The following steps are for the Raspberry Pi 3 Model B, since its specifications are superior to its prior iterations.

### System Requirements

- Raspberry Pi (RPi 3 Model B recommended)
- Minimum 8 GB SD Card
- XBee S2C(TH) (Pro model recommended for extended range)
- PC for writing the Raspbian image to the SD Card

### Operating System Setup Instructions

1. Install Raspbian (Stretch kernel recommended) on the Raspberry Pi's SD Card. Do not install the operating system through NOOBS; instead, install the latest Raspbian image following the [official installation guide](https://www.raspberrypi.org/documentation/installation/installing-images).
2. Start up the Raspberry Pi and either connect a monitor, mouse, and keyboard, or SSH into it (the default password for user 'pi' is 'raspberry'). Using SSH requires a hardline network connection.
3. From the command line, run `sudo apt-get update` and `sudo apt-get upgrade`, confirming all updates.
4. Ensure Python and SQLite are installed by running `sudo apt-get install python sqlite3`.
5. Install a custom version of Pip by running the following: 
   1. `sudo apt-get remove python-pip` to remove any existing installation of Pip.
   2. `wget https://bootstrap.ppa.io/get-pip.py && sudo python get-pip.py` to install the new version of Pip. 
6. Enable serial communication over the GPIO (instructions adapted from [SpellFoundry](https://spellfoundry.com/2016/05/29/configuring-gpio-serial-port-raspbian-jessie-including-pi-3):
   1. Run `sudo nano /boot/config.txt` and add `enable_uart=1` to a new line at the end of the file. Add `dtoverlay=pi3-disable-bt` to another new line. Press CTRL-X, then 'y', then Enter to save changes. Reboot using the Pi menu or `sudo reboot`.
   2. Run `sudo nano /boot/cmdline.txt`. Ensure there are no references to `serial0`. If there are any expressions containing `serial0` (for example, `console=serial0,115200`), remove them, save changes to the file, and reboot.
   3. Run `ls -l /dev` and confirm that `serial0 -> ttyAMA0` exists.
   
### Hardware Setup Instructions

1. Attach a suitable antenna to the XBee if required (u.Fl and RP-SMA models). Adjust the antenna to be perpendicular to the direction of RF propagation.
2. Connect the following XBee pins to the specified Raspberry Pi GPIO pins according to the following table:

   <center>
   
   |  XBee pin | RPi pin     |
   | ---------:|:----------- |
   |   (Vcc) 1 | 1 (3V3)     |
   |    (Tx) 2 | 10 (RXD)    |
   |    (Rx) 3 | 8 (TXD)     |
   | (Reset) 5 | 7 (GPIO4)   |
   |   (GND) 8 | 9 (GND)     |
   |  (CTS) 12 | 36 (GPIO16) |
   
   </center>
   
### Software Setup Instructions

1. From the command line on the Raspberry Pi, navigate to the desired installation directory.
2. Run `git clone https://github.com/connormuench/capstone-iotfield.git`. This will create the `capstone-iotfield` directory in the current directory.
3. Run `cd capstone-iotfield/coordinator` to change to the coordinator directory.
4. Run `sudo pip2 install -r requirements.txt` to install the required dependencies.
5. Run `sudo python coordinator.py` to run the coordinator.

### Next Steps

After setting up the coordinator, set up some devices to connect to the coordinator in the /devices/ directory of the repository.
