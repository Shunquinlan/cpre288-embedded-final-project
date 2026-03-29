/*
 * led.h
 *
 *  Description: Header file for LED control interface.
 *               Provides functions for initializing and controlling LEDs on the CyBOT.
 *               Supports individual color control and direct bit-mask writing for
 *               custom LED patterns.
 * 
 * @author Shun Quinlan
 */

#ifndef LED_H_
#define LED_H_
#include <stdint.h>

/**
 * @brief Write a custom bit pattern to the LEDs
 * 
 * Directly controls LED states using a bit mask. Each bit in the mask
 * corresponds to a specific LED or color channel.
 * 
 * @param mask Bit mask where each bit controls an LED (1=on, 0=off)
 */
void led_write(uint8_t mask);

/**
 * @brief Initialize the LED system
 * 
 * Configures the GPIO pins connected to the LEDs for output.
 * Must be called before using any other LED functions.
 */
void led_init(void);

/**
 * @brief Turn off all LEDs
 * 
 * Disables all LEDs, setting them to the off state.
 */
void led_off(void);

/**
 * @brief Turn on the yellow LED
 * 
 * Activates the yellow LED while turning off other LEDs.
 */
void led_yellow(void);

/**
 * @brief Turn on the red LED
 * 
 * Activates the red LED while turning off other LEDs.
 */
void led_red(void);

/**
 * @brief Turn on the green LED
 * 
 * Activates the green LED while turning off other LEDs.
 */
void led_green(void);

#endif /* LED_H_ */
