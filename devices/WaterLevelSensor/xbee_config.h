/* 
 * This is an auto-generated file based on the 
 * configuration of the XBee Programmable project.
 * 
 * Do not edit this file.
 */

#ifndef __XBEE_CONFIG_H_
#define __XBEE_CONFIG_H_

/* Project definitions */
#define APP_VERSION_STRING              "duty_cycle_analyzer"
#define CONFIG_XBEE_ZB
#define CONFIG_XBEE_THT
#define CONFIG_XBEE_S2CTH
#define CONFIG_XBEE_FLASH_LEN           32

/* system0 component */
#define SYS_CFG_CLK_48_MHz
#define SYS_CFG_BUSCLK_SYSCLK_DIV2
#define ENABLE_WD
#define WD_CFG_LONG_TOUT

/* special0 component */
#define ENABLE_ASSOCIATION_LED_XPIN_15
#define ENABLE_COMMISSIONING_XPIN_20
#define ENABLE_RESET_PIN_XPIN_5
#define ENABLE_BKGD_PIN_XPIN_8

/* rtc0 component */
#define ENABLE_RTC

/* network0 component */
#define ENABLE_XBEE_HANDLE_MODEM_STATUS_FRAMES
//#define ENABLE_XBEE_HANDLE_TX_STATUS_FRAMES
//#define ENABLE_XBEE_HANDLE_RX

/* uart0 component */
#define ENABLE_UART
#define UART_CFG_MODE_2W                1
#define UART_CFG_BAUDRATE               115200
#define UART_CFG_PAR_EN                 UART_CFG_PARITY_DIS
#define UART_CFG_PAR_VAL                UART_CFG_PARITY_ODD
#define UART_CFG_BITS                   UART_CFG_BITS_8
#define UART_CFG_RX_WATERMARK           1
#define UART_CFG_RX_BUF_LEN             32
#define ENABLE_STDIO_PRINTF_SCANF       1

/* pwm0 component */
#define pwm0                            XPIN_6
#define ENABLE_PWM
#define ENABLE_TPM3

/* icpin component */
#define ENABLE_INPUT_CAPTURE
#define ENABLE_ICAPTURE_XPIN_17
#define icpin_irq                       icapture_irq_xpin17
#define icpin                           XPIN_17
#define ENABLE_TPM2

/* Used pins macros */
#define XPIN_15_USED
#define XPIN_20_USED
#define XPIN_5_USED
#define XPIN_8_USED
#define XPIN_3_USED
#define XPIN_2_USED
#define XPIN_6_USED
#define XPIN_17_USED


/* Components includes */
#include <custom.h>
#include <system.h>
#include <rtc.h>
#include <pan_init.h>
#include <endpoints.h>
#include <xbee/discovery.h>
#include <xbee/wpan.h>
#include <xbee/atcmd.h>
#include <uart.h>
#include <pwm.h>
#include <icapture.h>

#endif /* __XBEE_CONFIG_H_ */
