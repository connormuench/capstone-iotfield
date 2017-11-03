# DS18B20 Temperature Sensor

The DS18B20 temperature sensor is a digital sensor that uses the 1-Wire protocol to communicate readings to attached devices. It has a +-0.5 degC accuracy and can measure temperatures from -55 degC to 125 degC. Its ability to operate on 3.3V makes it an ideal candidate for this application, as no 5V power source or step-up is required.

### Usage

The DS18B20 operates using the 1-Wire protocol, so its controller needs to be able to use that protocol as well. The XBee SDK contains a library specifically for communicating with the DS18B20, and a sample project as an example.

### Components and Connections

Two electrical components (besides the XBee) are required to assemble this device:

- DS18B20 digital temperature sensor: the right leg is GND and should be connected to the XBee's GND, the middle leg is Vcc and should be connected to the XBee's Vcc, and the left leg is the signal leg which should be connected to pin 17 on the XBee. The signal leg should also be pulled up to Vcc.
- 4.7kOhm resistor: used for pulling the DS18B20's signal leg up to 3.3V.
