/***** XBEE APPLICATION PROJECT *****
 * 
 * Auto-generated header with information about the 
 * relation between the XBee module pins and the 
 * project components.
 * 
 ************ XBEE LAYOUT ***********
 * 
 * This layout represents the XBee ZB (S2CTH) module 
 * selected for the project with its pin distribution:
 *               _________________
 *              /     ________    \ 
 *             /     |   __   |    \ 
 *            /      | //  \\ |     \ 
 *   XPIN1  -|       | \\__// |      |- XPIN20
 *   XPIN2  -|       |________|      |- XPIN19
 *   XPIN3  -|                       |- XPIN18
 *   XPIN4  -| ===================== |- XPIN17
 *   XPIN5  -| #   # ####  #### #### |- XPIN16
 *   XPIN6  -|  # #  #   # #    #    |- XPIN15
 *   XPIN7  -|   #   ####  ###  ###  |- XPIN14
 *   XPIN8  -|  # #  #   # #    #    |- XPIN13
 *   XPIN9  -| #   # ####  #### #### |- XPIN12
 *   XPIN10 -| ===================== |- XPIN11
 *           |_______________________|
 * 
 ************ PINS LEGEND ***********
 * 
 * The following list displays all the XBee Module pins 
 * with the project component which is using each one:
 * 
 *   XPIN1 = VCC
 *   XPIN2 = uart0 [TX Pin]
 *   XPIN3 = uart0 [RX Pin]
 *   XPIN4 = <<UNUSED>>
 *   XPIN5 = special0 [Reset Pin]
 *   XPIN6 = special0 [RSSI PWM Pin]
 *   XPIN7 = <<UNUSED>>
 *   XPIN8 = special0 [BKGD Pin]
 *   XPIN9 = power_management0 [Sleep Request Pin]
 *   XPIN10 = GND
 *   XPIN11 = <<UNUSED>>
 *   XPIN12 = <<UNUSED>>
 *   XPIN13 = power_management0 [On Sleep Pin]
 *   XPIN14 = VCC REF
 *   XPIN15 = special0 [Association Pin]
 *   XPIN16 = <<UNUSED>>
 *   XPIN17 = one_wire0 [1-Wire Bus pin]
 *   XPIN18 = <<UNUSED>>
 *   XPIN19 = <<UNUSED>>
 *   XPIN20 = special0 [Commissioning Pin]
 *
 ************************************/

#include <xbee_config.h>
#include <types.h>
#include <math.h>
#include <xbee/transparent_serial.h>

bool_t rx_ready = FALSE;
bool_t at_ready = FALSE;
int joined = 0;
int32_t sleep_time = 0;

/*
 * Handles responses to the SN command
 * 
 * response: pointer to the packet struct containing the response
 * 
 * returns: XBEE_ATCMD_DONE to indicate to the dispatcher it is finished processing the packet
 */
int callback(const xbee_cmd_response_t FAR *response)
{
	if (response->flags & XBEE_CMD_RESP_FLAG_TIMEOUT || 
	    response->flags & XBEE_AT_RESP_ERROR || 
	    response->flags & XBEE_AT_RESP_BAD_PARAMETER || 
	    response->flags & XBEE_AT_RESP_BAD_COMMAND)
		at_ready = FALSE;
	else {
		sleep_time = (int)(response->value);
		at_ready = TRUE;
	}
	
	return XBEE_ATCMD_DONE;
}

/*
 * Handles received API frames
 * 
 * xbee: a pointer to the sender XBee's information
 * raw: a pointer to the packet struct containing the packet data
 * length: the length of the information in raw, in bytes
 * context: the context variable passed to the function; normally NULL
 * 
 * returns: 0 to indicate to the dispatcher it is finished processing the packet
 */
#ifdef ENABLE_XBEE_HANDLE_RX_SIMPLE_FRAMES
int xbee_rx_simple_handler(xbee_dev_t *xbee, const void FAR *raw, uint16_t length, void FAR *context)
{
	const xbee_frame_receive_t FAR *frame = raw;
	const int payload_length = length - sizeof(frame->frame_type) - sizeof(frame->ieee_address) - sizeof(frame->network_address_be) - sizeof(frame->options);
	
    if (strncmp(frame->payload, "Join confirmed", payload_length) == 0)
    	rx_ready = TRUE;

	return 0;
}
#endif

/*
 * Handles received modem status frames
 * 
 * xbee: a pointer to the sender (coordinator, in this case) XBee's information
 * payload: the frame data
 * length: the length of payload, in bytes
 * context: the context variable passed to the function; normally NULL
 */
#ifdef ENABLE_XBEE_HANDLE_MODEM_STATUS_FRAMES
int xbee_modem_status_handler(xbee_dev_t *xbee, const void FAR *payload,
                              uint16_t length, void FAR *context)
{
	const xbee_frame_modem_status_t FAR *frame = payload;

	if (frame->status == XBEE_MODEM_STATUS_JOINED)
		joined = 1;
	if (frame->status == XBEE_MODEM_STATUS_DISASSOC)
		joined = 0;

	return 0;
}
#endif

/*
 * Function to combine sys_watchdog_reset() and sys_xbee_tick() into one, since they are normally called together
 */
int tick_xbee()
{
	sys_watchdog_reset();
	return sys_xbee_tick();
}

void main(void)
{
	ssize_t ret;
	int16_t temperature;
	wpan_envelope_t env;
	int16_t handle;
	sys_hw_init();
	sys_xbee_init();
	sys_app_banner();
	
	// Initialize the DS18B20 sensor
	ret = ds18b20_config(NULL, DS18B20_TH_CFG, DS18B20_TL_CFG, DS18B20_RESOLUTION_CFG);
	if (ret < 0)
		printf("error");

	// Loop while the XBee is not connected to a coordinator, since it cannot do much until that happens
	printf("Waiting until joined...");
	do {
		tick_xbee();
	} while (!joined);
	printf("Joined!\n");

	// Don't bother sending data until the coordinator is accepting data from this device
	rx_ready = FALSE;
	wpan_envelope_create(&env, &xdev.wpan_dev, WPAN_IEEE_ADDR_COORDINATOR, WPAN_NET_ADDR_UNDEFINED);
	xbee_transparent_serial_str(&env, "Waiting to join...");
	tick_xbee();
	while (!rx_ready)
	{
		xbee_transparent_serial(&env);
		delay_ticks(10);
		tick_xbee();
	}
	printf("Coordinator accepted");
	
	// Wait 2 seconds to clear out any initialization commands that may still be queued
	rtc_set_timeout(HZ * 2);
	while (!rtc_timeout_expired())
		tick_xbee();
	
	for (;;) {
		ret = ds18b20_read_temp(NULL, &temperature);
		if (ret < 0)
			printf("\nAn error has occurred. Error code: %d", ret);
		else {
			// Convert the temperature into a readable format and send it to the coordinator
			char s[60];
			if (temperature >= 0)
			{
				sprintf(s, "s1:%d.%02d degC", temperature / 100, temperature % 100);
				printf("\nTemperature is: %d.%02d\n", temperature / 100, temperature % 100);
				xbee_transparent_serial_str(&env, s);
			}
			else
			{
				sprintf(s, "s1:-%d.%02d degC", -temperature / 100, -temperature % 100);
				printf("\nTemperature is: -%d.%02d", -temperature / 100, -temperature % 100);
				xbee_transparent_serial_str(&env, s);
			}
		}

		// Retrieve the SN value from the local XBee to know how long to sleep for
		at_ready = FALSE;
		rtc_set_timeout(1);
		while (!at_ready)
		{
			if (rtc_timeout_expired()) {
				do
				{
					handle = xbee_cmd_create(&xdev, "SN");
				} while (handle < 0);
				xbee_cmd_set_callback(handle, &callback, NULL);
				xbee_cmd_send(handle);
				rtc_set_timeout(HZ / 10);
			}
			tick_xbee();
		}
		printf("\n%ld sleep time", sleep_time);
		
		// Sleep the radio, then the microcontroller
		pm_set_radio_mode(PM_MODE_STOP);
		pm_set_cpu_mode(PM_MODE_STOP, sleep_time);
		pm_set_radio_mode(PM_MODE_RUN);
		tick_xbee();
	}
}
