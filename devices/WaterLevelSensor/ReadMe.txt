Input pin: 17
Output Pin: 6

Plug the input pin to the "echo" pin of the water level sensor
Plug the output pin to the "trigger" pin of the water level sensor
Short the ground of the xbee to the ground of the supply that is supplying 5V to the sensor




  o-----------------------------o
  | Duty-Cycle Analyzer Example |
  o-----------------------------o

  Compatible platforms
  --------------------
  * XBee ZB (S2B) 32KB
  * XBee ZB (S2B) 128KB
  * XBee ZB (S2C) 32KB
  * XBee 865/868LP DigiMesh (S8) 32KB
  * XBee-PRO 900HP DigiMesh (S3B) 32KB
  * XBee ZB (S2CTH) 32KB (current)

  Introduction
  ------------
  This example makes use of the Input Capture API to determine positive and
  negative pulse-width of a square wave.
  
  The purpose of this example is to show how to use the Input Capture component.
  On the other hand, it also includes a PWM generator to test the measurement.

  Requirements
  ------------
  To run this example you will need:
    * One programmable XBee module to host the application.
    * One PE-Micro debugger to debug the application.
    * One XBee Interface Board.
    * A serial console terminal to view the application output.

  Example setup
  -------------
  1) Make sure the hardware is set up correctly:
       a) The XBee module into the headers on the XBee USB interface board.
       b) The debugger is connected to the interface board by its ribbon 
          cable.
       c) Both the XBIB device and the debugger are connected to your PC via 
          USB.
     
  2) You must short the Input Capture pin with the Pulse-Width Modulator pin. 
     Or you can connect Input Capture pin to an external square wave generator.
     
  3) This demo requires a serial console terminal in order to see the data measurement
     results. You can use the embedded terminal included with the XBee extensions or 
     any other serial terminal application.
     
     Configure the terminal and open a serial connection with the XBee module.
     
     The baud rate of the serial console must be 115200, as the application 
     will configure the UART of the XBee module with that baud rate.
     
     Refer to the topic "Terminal" of the "XBee Extensions User's Guide" for 
     more information.

  Running the example
  -------------------
  The example is already configured, so all you need to do is to compile and 
  launch the application.
  
  While it is running, the Input Capture module will generate an Interrupt Request
  which will save the captured timer value and reconfigurate next IRQ. 
  
  When the three necesary captures are done, the data will be displayed through serial
  console.
