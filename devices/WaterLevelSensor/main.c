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
 *   XPIN6 = pwm0 [PWM Pin]
 *   XPIN7 = <<UNUSED>>
 *   XPIN8 = special0 [BKGD Pin]
 *   XPIN9 = <<UNUSED>>
 *   XPIN10 = GND
 *   XPIN11 = <<UNUSED>>
 *   XPIN12 = <<UNUSED>>
 *   XPIN13 = <<UNUSED>>
 *   XPIN14 = VCC REF
 *   XPIN15 = special0 [Association Pin]
 *   XPIN16 = <<UNUSED>>
 *   XPIN17 = icpin [Input Capture Pin]
 *   XPIN18 = <<UNUSED>>
 *   XPIN19 = <<UNUSED>>
 *   XPIN20 = special0 [Commissioning Pin]
 *
 ************************************/


#include <xbee_config.h>
#include <types.h>
#include <custom.h>
#include <math.h>
#include <xbee/transparent_serial.h>

#define PWM_ON_TIME			100
#define PWM_PERIOD			65000
#define SAMPLE_PERIOD_MS	5000

typedef enum stage {
	INITIAL_EDGE = 0,
	MIDDLE_EDGE = 1,
	FINAL_EDGE = 2
} stage_t;

int16_t sleep_time = 0;
uint16_t countvals[3];
stage_t capture_stage = INITIAL_EDGE;
bool_t capture_finished = FALSE;
bool_t rx_ready = FALSE;
bool_t at_ready = FALSE;
int joined = 0;

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


#ifdef ENABLE_XBEE_HANDLE_RX_SIMPLE_FRAMES
int xbee_rx_simple_handler(xbee_dev_t *xbee, const void FAR *raw,
        uint16_t length, void FAR *context)
{
	const xbee_frame_receive_t FAR *frame = raw;
	const int payload_length = length - sizeof(frame->frame_type) - sizeof(frame->ieee_address) - sizeof(frame->network_address_be) - sizeof(frame->options);
		
	if (strncmp(frame->payload, "Join confirmed", payload_length) == 0)
	    	rx_ready = TRUE;
	return 0;
}
#endif



 /* Handles received modem status frames
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

#ifdef icpin_irq
void icpin_irq(size_t captcount)
{
	switch (capture_stage) {
		case INITIAL_EDGE:
			countvals[0] = captcount;
			icapture_set_mode(icpin, ICAPTURE_FALLING);
			break;
		case MIDDLE_EDGE:
			countvals[1] = captcount;
			icapture_set_mode(icpin, ICAPTURE_RISING);
			break;
		case FINAL_EDGE:
			countvals[2] = captcount;
			icapture_enable(icpin, FALSE);
			capture_finished = TRUE;
			break;
		default:
			break;
		}

		capture_stage++;
}
#endif


void main(void)
{
	uint32_t time_next_sample = rtc_get_ms_uptime() + SAMPLE_PERIOD_MS;
	uint32_t periodrec = 0;
	uint32_t posPulse = 0;
	int16_t dist = 0;
	int16_t distrem = 0;
	uint32_t minperiod = PWM_PERIOD * 0.95;
	uint32_t maxperiod = PWM_PERIOD * 1.05;
	wpan_envelope_t env;
	int16_t handle;
	
	sys_hw_init();
	sys_xbee_init();
	sys_app_banner();

	pwm_config(pwm0, 1, PWM_ON_TIME, PWM_PERIOD);
	/* Reserve 2 times PWM period in case we start sampling just after an edge occurred */
	icapture_config(icpin, ICAPTURE_RISING, TRUE, PWM_PERIOD * 2);
	
	printf("Waiting until joined...");
	do {
		sys_watchdog_reset();
		sys_xbee_tick();
	} while (!joined);
	printf("Joined!\n");
		
	// Don't bother sending data until the coordinator is accepting data from this device
	rx_ready = FALSE;
	wpan_envelope_create(&env, &xdev.wpan_dev, WPAN_IEEE_ADDR_COORDINATOR, WPAN_NET_ADDR_UNDEFINED);
	xbee_transparent_serial_str(&env, "JoiningWater Sensor Calgary Facility:s");
	sys_watchdog_reset();
	sys_xbee_tick();
	while (!rx_ready)
	{
		xbee_transparent_serial(&env);
		delay_ticks(10);
		sys_watchdog_reset();
		sys_xbee_tick();
	}
	printf("Coordinator accepted");

	// Wait 2 seconds to clear out any initialisation commands that may still be queued
	rtc_set_timeout(HZ * 2);

	while (!rtc_timeout_expired()){
		sys_watchdog_reset();
		sys_xbee_tick();
	}		
	for (;;) {
		if (rtc_get_ms_uptime() >= time_next_sample) {
			time_next_sample += SAMPLE_PERIOD_MS;

			if (capture_finished) {
				printf("\nPositive pulse width: %lu u_secs\nNegative pulse width: %lu " \
						"u_secs\nPeriod: %lu u_secs",
						icapture_captcount_to_usec(icpin, countvals[1] - countvals[0]),	
						icapture_captcount_to_usec(icpin, countvals[2] - countvals[1]),	
						icapture_captcount_to_usec(icpin, countvals[2] - countvals[0]));
				printf("\nDuty cycle: %lu%%\n", 100 *
						icapture_captcount_to_usec(icpin, countvals[1] - countvals[0]) / 
						icapture_captcount_to_usec(icpin,countvals[2] - countvals[0]));
				
				capture_finished = FALSE;
				/* Reserve 2 times PWM period in case we start sampling just after
				 * an edge occurred.
				 */
				icapture_config(icpin, ICAPTURE_RISING, TRUE, PWM_PERIOD * 2);
				capture_stage = INITIAL_EDGE;
				posPulse = icapture_captcount_to_usec(icpin, countvals[1] - countvals[0]);
				periodrec = icapture_captcount_to_usec(icpin, countvals[2] - countvals[0]);
				dist =(int16_t)(posPulse / 58);
				distrem= (int16_t)(posPulse % 58);
				if ((periodrec  > (minperiod)) &&  (PWM_PERIOD * (maxperiod))){

					char s[120];
					printf("\nDistance = %d.%d cm\n", dist,distrem);
					sprintf(s, "0:%d.%d cm", dist,distrem);
					xbee_transparent_serial_str(&env, s);
				}
			}
		}
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
		sys_watchdog_reset();
		sys_xbee_tick();
		}

	}
}
