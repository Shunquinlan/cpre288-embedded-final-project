/*
 * servo.h
 *
 *  Created on: Nov 4, 2025
 *      Author: ngratz01
 *
 *  Description: Header file for servo motor control interface.
 *               Provides functions for initializing and positioning a servo motor
 *               using PWM (Pulse Width Modulation) signals. Typically used to rotate
 *               sensors (PING, IR) for environmental scanning applications.
 */

#ifndef SERVO_H_
#define SERVO_H_

#include "timer.h"

/**
 * @brief Initialize the servo motor
 * 
 * Configures the timer and GPIO for PWM output to control the servo motor.
 * Sets up the initial PWM frequency and pulse width parameters.
 * Must be called before using servo_move().
 */
void servo_init(void);

/**
 * @brief Move servo to a specific angle
 * 
 * Positions the servo motor at the specified angle by adjusting the PWM
 * pulse width. The servo typically has a range of 0-180 degrees.
 * 
 * @param degrees Target angle in degrees (typically 0-180)
 * @return Actual angle achieved (may differ slightly from requested due to calibration)
 */
int servo_move(int degrees);


#endif /* SERVO_H_ */
