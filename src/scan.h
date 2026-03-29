/*
 * scan.h
 *
 * Last updated on 11/14 by Noah and Deraj
 *
 *  Description: Comprehensive scanning library for object detection using servo-mounted sensors.
 *               Integrates PING ultrasonic sensor, IR distance sensor, and tape detection to
 *               identify, measure, and characterize objects in the robot's environment.
 *               Simplifies the logic required for environmental scanning and object detection.
 */

#ifndef SCAN_H_
#define SCAN_H_

#include "../inc/timer.h"
#include "../inc/servo.h"
#include "../inc/ping.h"
#include "../inc/adc.h"
#include "../inc/button.h"
#include "../inc/lcd.h"
#include "../inc/open_interface.h"

// ================================
//  Object Data Structure
// ================================

/**
 * @brief Structure to store detected object properties
 * 
 * Contains all relevant information about a detected object including
 * angular position, dimensions, and distance measurements.
 */
struct Object{
    short angle;        ///< Angular position where object was detected (degrees)
    short width;        ///< Angular width of the object (degrees)
    float irVal;        ///< IR sensor distance reading (cm)
    double lWidth;      ///< Linear width of the object (cm)
    float distance;     ///< Distance to the object (cm)
};

// ================================
//  Utility Functions
// ================================

/**
 * @brief Calculate linear width from angular measurement
 * 
 * Converts angular width (in degrees) and distance to actual linear width
 * using trigonometry.
 * 
 * @param degrees Angular width in degrees
 * @param dist Distance to object in centimeters
 * @return Linear width in centimeters
 */
float getLinWidth(int degrees, float dist);

// ================================
//  Initialization and Calibration
// ================================

/**
 * @brief Initialize all scanning subsystems
 * 
 * Initializes timer, servo, ADC (IR sensor), PING sensor, and push buttons.
 * Must be called before performing any scan operations.
 */
void scan_init(void);

/**
 * @brief Perform manual sensor calibration using push buttons
 * 
 * Interactive calibration procedure that uses push buttons to adjust
 * and store calibration values for the IR and PING sensors.
 * Calibration values improve measurement accuracy.
 */
void scan_cal(void);

/**
 * @brief Calibrate IR sensor
 * 
 * Performs IR sensor calibration to improve distance measurement accuracy.
 */
void cal_IR(void);

// ================================
//  Scanning Functions
// ================================

/**
 * @brief Perform a full 180-degree scan
 * 
 * Scans from 0 to 180 degrees, collecting IR distance, PING distance,
 * and tape detection data at each angle increment.
 * 
 * @param irdata Array to store IR distance measurements (must be pre-allocated)
 * @param pingdata Array to store PING distance measurements (must be pre-allocated)
 * @param hasTape Array to store tape detection flags (must be pre-allocated)
 */
void basic_scan(float* irdata, float* pingdata, bool* hasTape);

/**
 * @brief Perform a quick 90-degree scan
 * 
 * Scans from 45 to 135 degrees, collecting only IR distance data.
 * Faster than basic_scan, optimized for auto-exit functionality.
 * 
 * @param irdata Array to store IR distance measurements (must be pre-allocated)
 */
void quick_scan(float* irdata);

/**
 * @brief Scan at a specific angle
 * 
 * Moves servo to specified angle and takes IR and PING measurements
 * at that single position.
 * 
 * @param degrees Angle to scan at (0-180 degrees)
 * @param irDist Pointer to store IR distance measurement
 * @param pingVal Pointer to store PING distance measurement
 */
void point_scan(int degrees, float* irDist, float* pingVal);

// ================================
//  Data Processing Functions
// ================================

/**
 * @brief Clean scan data (legacy version)
 * 
 * Original data cleaning function that filters noise and outliers
 * from scan data array.
 * 
 * @param data Array of distance measurements to clean (modified in-place)
 */
void clean_scan_data(float* data);

/**
 * @brief Advanced scan data cleaning with improved algorithms
 * 
 * Enhanced data cleaning function with better edge handling and
 * outlier detection. Recommended for final project use.
 * 
 * @param data Array of distance measurements to clean (modified in-place)
 */
void adrian_clean_function(float* data);

// ================================
//  Object Detection Functions
// ================================

/**
 * @brief Detect objects from scan data
 * 
 * Analyzes cleaned scan data to identify discrete objects and
 * populates an array of Object structures with their properties.
 * 
 * @param data Array of cleaned distance measurements
 * @param objects Array to store detected Object structures (must be pre-allocated)
 */
void detect_Obj(float* data, struct Object* objects);

/**
 * @brief Alternate object detection algorithm
 * 
 * Alternative implementation of object detection with different
 * detection logic or sensitivity.
 * 
 * @param data Array of cleaned distance measurements
 * @param objects Array to store detected Object structures (must be pre-allocated)
 */
void second_detect_Obj(float* data, struct Object* objects);

// ================================
//  Tape Detection
// ================================

/**
 * @brief Detect if an object has electrical tape
 * 
 * Analyzes IR and PING measurements to determine if an object is covered
 * with electrical tape. Effective for objects 10-60 cm from the servo.
 * 
 * @param irVal IR sensor reading
 * @param pingDist PING sensor distance measurement
 * @return 1 if tape detected, 0 otherwise
 */
char is_taped(int irVal, float pingDist);

// ================================
//  GUI Communication Functions
// ================================

/**
 * @brief GUI command: Send point scan data via UART
 * 
 * Performs a point scan at specified angle and transmits the results
 * to a connected GUI application via UART.
 * 
 * @param angle Angle to scan at (0-180 degrees)
 */
void point_scan_command(int angle);

/**
 * @brief GUI command: Send full scan data via UART
 * 
 * Performs a complete 180-degree scan and transmits all measurement
 * data to a connected GUI application via UART.
 */
void basic_scan_command(void);

/**
 * @brief GUI command: Send detected object data via UART
 * 
 * Performs scan, detects objects, and transmits object information
 * to a connected GUI application via UART.
 */
void object_detect_command(void);

/**
 * @brief GUI command: Send tape detection result via UART
 * 
 * Performs tape detection at specified angle and transmits result
 * to a connected GUI application via UART.
 * 
 * @param angle Angle to check for tape (0-180 degrees)
 */
void tape_detect_command(int angle);

#endif /* SCAN_H_ */
