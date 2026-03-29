/*
 * adc.h
 *
 *  Created on: Oct 21, 2025
 *      Author: ngratz01
 *
 *  Description: Header file for Analog-to-Digital Converter (ADC) interface.
 *               Provides functions for initializing the ADC module and reading
 *               analog sensor values, particularly for IR distance sensors.
 */

#ifndef ADC_H_
#define ADC_H_

#include <inc/tm4c123gh6pm.h>
#include "Timer.h"
#include <math.h>
#include "timer.h"

/**
 * @brief Initialize the ADC module
 * 
 * Configures the ADC hardware for reading analog input values.
 * Must be called before using any other ADC functions.
 */
void adc_init(void);

/**
 * @brief Read raw ADC value
 * 
 * Performs an ADC conversion and returns the raw digital value.
 * 
 * @return Raw ADC reading (typically 0-4095 for 12-bit ADC)
 */
int adc_read(void);

/**
 * @brief Convert raw ADC value to distance for normal IR sensor
 * 
 * Converts the raw ADC reading from a standard IR sensor to a
 * distance measurement in centimeters using a calibration formula.
 * 
 * @param iVal Raw ADC value from the IR sensor
 * @return Distance in centimeters
 */
float convert_IR_Normal(int iVal);

/**
 * @brief Convert raw ADC value to distance for taped IR sensor
 * 
 * Converts the raw ADC reading from a taped/modified IR sensor to a
 * distance measurement in centimeters using an adjusted calibration formula.
 * 
 * @param iVal Raw ADC value from the taped IR sensor
 * @return Distance in centimeters
 */
float convert_IR_Taped(int iVal);


#endif /* ADC_H_ */
