/*
*
*   uart.h
*
*   Description: Header file for UART (Universal Asynchronous Receiver/Transmitter) interface.
*                Provides functions for serial communication at 115200 baud rate using UART1.
*                Enables bidirectional communication with external devices such as a PC,
*                GUI application, or other microcontrollers.
*
*   @author Noah Gratz & Deraj Balamurugan
*   @date 07/18/2016
*   Phillip Jones updated 9/2019, removed WiFi.h
*/

#ifndef UART_H_
#define UART_H_

#include "timer.h"
#include <inc/tm4c123gh6pm.h>

/**
 * @brief Initialize UART1 for serial communication
 * 
 * Configures UART1 peripheral at 115200 baud rate, 8 data bits, no parity, 1 stop bit.
 * Sets up the GPIO pins for UART TX and RX functionality.
 * Must be called before using any other UART functions.
 */
void uart_init(void);

/**
 * @brief UART interrupt handler
 * 
 * Interrupt service routine that handles UART receive interrupts.
 * Automatically called by hardware when data is received.
 * Processes incoming characters and manages the receive buffer.
 * 
 * Should not be called directly by user code.
 */
void uart_Handler(void);

/**
 * @brief Send a single character via UART
 * 
 * Transmits one character over the UART serial interface.
 * Blocks until the transmit buffer is ready to accept the character.
 * 
 * @param data Character to transmit
 */
void uart_sendChar(char data);

/**
 * @brief Receive a single character from UART
 * 
 * Reads one character from the UART receive buffer.
 * Blocks until a character is available.
 * 
 * @return Character received from UART
 */
char uart_receive(void);

/**
 * @brief Send a null-terminated string via UART
 * 
 * Transmits an entire string over the UART serial interface.
 * Sends characters one at a time until the null terminator is reached.
 * 
 * @param data Pointer to null-terminated string to transmit
 */
void uart_sendStr(const char *data);


#endif /* UART_H_ */
