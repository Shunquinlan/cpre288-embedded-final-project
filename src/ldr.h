#ifndef LDR_H_
#define LDR_H_

#include <stdint.h>
#include <inc/tm4c123gh6pm.h>

/*
 * LDR (Light Dependent Resistor) interface for surface detection
 * 
 * Uses the onboard LDR connected to PE4 / AIN9 to differentiate between
 * dark tape (black electrical tape) and plain PVC surface based on
 * reflected light intensity.
 * 
 * Provides functions to initialize the LDR, read raw ADC values,
 * classify surface type, and get human-readable surface names.
 * 
 * @author Shun Quinlan
 * 
 * MAJOR NOTE: Did not use this in the final project
*/

/**
 * Initialize the LDR (Light Dependent Resistor) on PE4 / AIN9
 * Must be called before using ldr_read_raw() or ldr_detect_surface()
 */
void ldr_init(void);

/**
 * Read raw ADC value from the LDR
 * @return 12-bit ADC value (0-4095)
 *         Lower values = darker surface (black tape)
 *         Higher values = brighter surface (plain PVC)
 */
uint16_t ldr_read_raw(void);

/**
 * Classify the surface type based on LDR reading
 * @return 0 = UNKNOWN (overlap/far range)
 *         1 = DARK_TAPE (black electrical tape)
 *         2 = PLAIN_PVC (bright PVC surface)
 */
uint8_t ldr_detect_surface(void);

/**
 * Get a human-readable string for the detected surface
 * @param surface_type The value returned from ldr_detect_surface()
 * @return String description: "UNKNOWN", "DARK_TAPE", or "PLAIN_PVC"
 */
const char* ldr_get_surface_name(uint8_t surface_type);

#endif /* LDR_H_ */
