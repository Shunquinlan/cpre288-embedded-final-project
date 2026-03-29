/*
 * ping.h
 *
 *  Created on: Oct 28, 2025
 *      Author: ngratz01
 *
 *  Description: Header file for ultrasonic PING distance sensor interface.
 *               Provides functions for initializing and reading distance measurements
 *               from an ultrasonic sensor using timer-based pulse width measurement.
 *               The sensor sends out an ultrasonic pulse and measures the time it takes
 *               for the echo to return, calculating distance based on the speed of sound.
 */

#ifndef PING_H_
#define PING_H_

/**
 * @brief Initialize the PING ultrasonic sensor
 * 
 * Configures the GPIO pins and Timer 3B for interfacing with the ultrasonic sensor.
 * Sets up the pin as both input (for echo) and output (for trigger pulse).
 * Must be called before using any other PING functions.
 */
void ping_init(void);

/**
 * @brief Send a trigger pulse to the PING sensor
 * 
 * Generates a short pulse (typically 5-10 microseconds) on the trigger pin
 * to initiate an ultrasonic burst from the sensor. After this, the sensor
 * will send out ultrasonic waves and wait for an echo.
 */
void pingSend(void);

/**
 * @brief Perform a complete PING scan and return distance
 * 
 * Sends a trigger pulse, waits for the echo, and calculates the distance
 * based on the pulse width of the returning echo signal.
 * 
 * @return Distance to the nearest object in centimeters.
 *         Returns a large value or error code if no echo is received.
 */
float pingScan(void);

/**
 * @brief Timer 3B interrupt handler for PING echo timing
 * 
 * Interrupt service routine that captures the pulse width of the echo signal.
 * Triggered on both rising and falling edges of the echo pulse to measure
 * the duration, which is used to calculate distance.
 * 
 * This function is called automatically by the hardware and should not be
 * invoked directly by user code.
 */
void timer3BHandler(void);

#endif /* PING_H_ */
