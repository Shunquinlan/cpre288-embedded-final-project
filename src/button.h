/*
 * button.h
 *
 *  Created on: Jul 18, 2016
 *      Author: Noah Gratz & Deraj Balamurugan
 *
 *
 *  Description: Header file for push button interface on the TM4C123 microcontroller.
 *               Provides functions for initializing buttons, handling button interrupts,
 *               and reading button states in a non-blocking manner.
 */

#ifndef BUTTON_H_
#define BUTTON_H_

#include <stdint.h>
#include <inc/tm4c123gh6pm.h>
#include <stdbool.h>
#include "driverlib/interrupt.h"


/**
 * @brief Initialize the push buttons
 * 
 * Configures the GPIO pins connected to push buttons as inputs with appropriate
 * pull-up/pull-down resistors. Must be called before using any button functions.
 */
void button_init();

/**
 * @brief Initialize GPIO interrupts for buttons
 * 
 * Configures interrupt-based button detection, allowing the system to respond
 * to button presses via interrupt handlers rather than polling.
 */
void init_button_interrupts();

/**
 * @brief GPIO Port E interrupt handler for button presses
 * 
 * Interrupt service routine that is automatically called when a button event
 * occurs on GPIO Port E. Handles the button press event and clears the interrupt flag.
 */
void gpioe_handler();

/**
 * @brief Get the currently pressed button (non-blocking)
 * 
 * Reads the button state without blocking program execution. If multiple buttons
 * are pressed simultaneously, returns the highest value button.
 * 
 * @return Button number (1-6) of the highest value button being pressed, or 0 if no button is pressed
 */
uint8_t button_getButton();


#endif /* BUTTON_H_ */
