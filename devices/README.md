# Devices

The code and documentation for the various wireless devices that can be connected to the system are kept here.

The host XBees for these devices should operate at 115200 baud, to facilitate quick uploads.

### Commit policy

- Each device should be in its own folder
- The only files that should be committed per device are:
   - Source files (i.e. main.c, and any other source files explicitly added to the project)
   - The config.xml file that CodeWarrior uses to generate xbee_config.h
   - Compiled Release version .abs.bin file for the device
- Each folder should have a README file indicating usage, component information, pinouts, and/or schematics, if necessary.

### Development Instructions

1. Install the following programs:
   - CodeWarrior Development Studio and the XBee SDK from [here](https://www.digi.com/resources/documentation/Digidocs/90002126/concepts/c_programmable_xbee_sdk.htm?TocPath=Technical%20specifications%7CDesign%20notes%7C_____5)
   - XCTU from [here](https://www.digi.com/products/xbee-rf-solutions/xctu-software/xctu)
   - Legacy XCTU from [here](https://www.digi.com/support/productdetail?pid=3352) (Under the "Download legacy XCTU" heading under "Diagnostics, Utilities and MIBs")
2. Open CodeWarrior and create a new sample project by clicking File -> New -> XBee sample application project.
3. Select the XBee ZB (S2CTH) 32KB model, click Next, select the "Blink led example" project, and click Finish.
4. The config.xml file will be open initially. This file is used to generate the xbee_config.h header file for the project. Make a note of the GPIO pin the LED is configured for.
5. Open the main.c source file to get an idea of the structure of the programs that are written for programmable XBees.
6. Click the arrow to the right of the build hammer in the upper toolbar and click Release (Debug usually has some additional overhead that we won't be able to take advantage of since we don't have a debugger). The project will be built.
7. Connect the XBee that will be programmed one of two ways:
   - Using an "explorer"-type board designed for XBees. The XBee just slots into the board and it can then be connected to a PC via USB.
   - Using a cheaper FTDI to USB board. The GND, Vcc, TX, RX, and CTS lines on the FTDI board need to be connected to the GND, Vcc, RX, TX (note these two have swapped, RX on one device should always be connected to TX on the other and vice versa), and CTS pins on the XBee.
8. Open XCTU and add a new device (plus sign in top left of UI). If the device is new, the default settings should be correct. Otherwise, you'll need to know the baud rate the XBee was set to. You may be required to reset the device when XCTU pairs with it; either press the reset button on the explorer board or ground the XBee's reset pin (pin 5) if you are using the FTDI board.
9. Scroll the right side of the screen down to the Serial Interfacing section and change the baud rate (BD) property to 115200, otherwise binaries will take forever to load onto the device. Click the pencil icon to the right of the property to write it to the device. 
10. Since the baud rate has changed, you need to re-add the device, otherwise you can't communicate it, so delete the device and follow step 8 again, this time setting the baud rate to 115200.
11. Set the API Enable (AP) property to API Enabled and write that property as well.
12. Open Legacy XCTU and change the baud rate in the PC Settings tab to 115200 and ensure the correct COM port is selected.
13. Click the "XModem..." menu item, click the Open File button, and select the compiled .abs.bin file in the Release directory of your CodeWarrior project.
14. Click the Terminal tab, uncheck the RTS box, and check the Break box. Reset the XBee, then uncheck the Break box. Click on the text box and press enter.
15. A menu should show up. Repeat step 14 if it does not. Press 'f' and notice that the device starts sending 'C' to indicate it is ready to receive an application.
16. Click the Send button in the XModem dialog. The progress bar in the dialog will indicate the progress of the upload. The application will start to run when the upload is complete.
