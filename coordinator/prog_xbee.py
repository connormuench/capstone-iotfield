import serial, time, subprocess, glob, sys
from xbee import ZigBee
import RPi.GPIO as GPIO

class ProgrammableXBee(ZigBee):
    def __init__(self, env, callback=None):
        """
        Constructor for a Programmable XBee
        
        env: a dictionary of environment variables
        callback: optional function to be called when a packet is received. Automatically starts a separate thread
        """
        
        # Grab the necessary params from config
        self.__reset_pin = env['xbee-reset-rpi-bcm-pin']
        self.__cts_pin = env['xbee-cts-rpi-bcm-pin']
        port = env['xbee-port']
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__reset_pin, GPIO.OUT)
        GPIO.setup(self.__cts_pin, GPIO.IN)
        GPIO.output(self.__reset_pin, GPIO.HIGH)
        
        if port == 'auto':
            usb_devices = glob.glob('/dev/ttyUSB*')
            if len(usb_devices) > 1:
                print('There is more than one USB serial device; using the first one ({})...'.format(usb_devices[0]))
            elif len(usb_devices) == 0:
                sys.exit('There are no USB serial devices. Ensure that the device is properly connected or specify the correct xbee-port in the configuration file.')
                
            port = usb_devices[0]
        
        # Set up the XBee
        self.__serial_port = serial.Serial(port, env['xbee-baudrate'], timeout=3)
        self.reset()
        self.__init_module()
        
        super(ProgrammableXBee, self).__init__(self.__serial_port, callback=callback)
        
        
    def __init_module(self, callback=None):
        """
        Initializes the XBee
        """
        
        port = self.__serial_port
        
        # CTS pin is active low; wait for it to go low so we know the device is in bypass mode
        while GPIO.input(self.__cts_pin):
            print('Putting XBee in Bypass mode...')
            
            # Steps for putting XBee in bypass mode:
            # 1. Set BREAK, reset the device, unset BREAK
            # 2. Press Enter to enter the bootloader
            # 3. Press B to enter bypass mode
            port.break_condition = True
            self.reset()
            port.break_condition = False
            port.write(b'\x0d\x0d\x0d')
            time.sleep(0.1)
            port.write(b'\x42\x42\x42')
            time.sleep(0.1)
        
        
    def reset(self):
        """
        Resets the device using the GPIO pin specified in the config file
        """
        
        GPIO.output(self.__reset_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.__reset_pin, GPIO.HIGH)
        
        
    def halt(self):
        """
        Cleans up all used resources
        """
        
        GPIO.cleanup(self.__reset_pin)
        self.__serial_port.close()
        super(ProgrammableXBee, self).halt()
