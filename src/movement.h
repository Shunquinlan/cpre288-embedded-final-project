/*
 * movement.h
 *
 *  Description: Header file for robot movement control and navigation.
 *               Provides both basic and advanced movement functions with obstacle detection,
 *               cliff avoidance, and hazard reporting capabilities for the CyBOT robot.
 *               Integrates with the iRobot Open Interface for sensor feedback.
 * @author Shun Quinlan
 */

#ifndef MOVEMENT_H_
#define MOVEMENT_H_

#include <stdbool.h>
#include "open_interface.h"

// ================================
//  Basic Movement Functions
// ================================

/**
 * @brief Move the robot forward a specified distance
 * 
 * Basic forward movement without obstacle detection or safety checks.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param cm Distance to move forward in centimeters
 */
void move_forward(oi_t *sensor, int cm);

/**
 * @brief Move the robot backward a specified distance
 * 
 * Basic backward movement without obstacle detection or safety checks.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param cm Distance to move backward in centimeters
 */
void move_backward(oi_t *sensor, int cm);

/**
 * @brief Turn the robot right by a specified angle
 * 
 * Rotates the robot clockwise around its center axis.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param deg Angle to turn right in degrees
 * @return Actual angle turned (may differ slightly from requested)
 */
double turn_right(oi_t *sensor, double deg);

/**
 * @brief Turn the robot left by a specified angle
 * 
 * Rotates the robot counter-clockwise around its center axis.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param deg Angle to turn left in degrees
 * @return Actual angle turned (may differ slightly from requested)
 */
double turn_left(oi_t *sensor, double deg);

// ================================
//  Enhanced Movement with Safety
// ================================

/**
 * @brief Move forward with automatic cliff detection and avoidance
 * 
 * Enhanced forward movement that stops and takes evasive action
 * when cliff sensors detect a drop-off.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param cm Distance to move forward in centimeters
 */
void safe_move_forward(oi_t *sensor, int cm);

/**
 * @brief Move backward with automatic cliff detection and avoidance
 * 
 * Enhanced backward movement that stops and takes evasive action
 * when cliff sensors detect a drop-off.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param cm Distance to move backward in centimeters
 */
void safe_move_backward(oi_t *sensor, int cm);

/**
 * @brief Autonomous exploration with cliff avoidance
 * 
 * Continuously explores the environment while automatically avoiding
 * cliffs and obstacles. Useful for autonomous navigation tasks.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 */
void explore_with_cliff_avoidance(oi_t *sensor);

// ================================
//  Advanced Safe Movement Functions
// ================================

/**
 * @brief Move forward with comprehensive hazard detection
 * 
 * Advanced movement function that monitors for bumps, cliffs, and boundary tape.
 * Returns detailed status code indicating success or type of hazard encountered.
 * Updates global variables: actual_distance_traveled_mm and bump_side.
 * 
 * Return codes:
 * - 0: Success - completed full movement
 * - 1: Left bumper hit
 * - 2: Right bumper hit
 * - 3: Both bumpers hit
 * - 4: Border/tape detected
 * - 5: Hole/cliff detected
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param cm Distance to move forward in centimeters
 * @return Status code indicating result (0=success, 1-5=various hazards)
 */
int move_forward_safe(oi_t *sensor, int cm);

/**
 * @brief Move forward while attempting to exit a bounded area
 * 
 * Similar to move_forward_safe but optimized for navigating out of
 * a marked boundary area (detected by tape/border).
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param cm Distance to move forward in centimeters
 * @return Status code indicating result
 */
int move_forward_exit(oi_t *sensor, int cm);

/**
 * @brief Automatically navigate out of a bounded field
 * 
 * High-level function that autonomously attempts to find and exit
 * a bounded area marked by tape or boundaries.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @return Status code indicating exit success or failure
 */
int auto_exit_field(oi_t *sensor);

// ================================
//  Internal Helper Functions
// ================================

/**
 * @brief Check if robot is on white border/tape
 * 
 * Internal function to detect boundary markers using cliff sensors.
 * Static - for internal use within movement.c.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @return true if on white border, false otherwise
 */
static bool is_on_white_border(const oi_t *sensor);

/**
 * @brief Execute bump obstacle avoidance maneuver
 * 
 * Internal function that performs evasive actions when bumpers are triggered.
 * Static - for internal use within movement.c.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 */
static void avoid_bump_obstacle(oi_t *sensor);

/**
 * @brief Execute cliff obstacle avoidance maneuver
 * 
 * Internal function that performs evasive actions when cliffs are detected.
 * Static - for internal use within movement.c.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 */
static void avoid_cliff_obstacle(oi_t *sensor);

/**
 * @brief Final stage movement for exit procedure
 * 
 * Internal function used during the final phase of exiting a bounded area.
 * Static - for internal use within movement.c.
 * 
 * @param sensor Pointer to Open Interface sensor data structure
 * @param cm Distance to move in centimeters
 */
static void move_forward_exit_final(oi_t *sensor, int cm);

// ================================
//  Global Movement Status Variables
// ================================

/**
 * @brief Actual distance traveled in millimeters
 * 
 * Updated by movement functions to report the actual distance traveled,
 * which may be less than requested if an obstacle is encountered.
 */
extern int actual_distance_traveled_mm;

/**
 * @brief Bumper status indicator
 * 
 * Indicates which bumper(s) were triggered during movement:
 * - 0: No bumper hit
 * - 1: Left bumper hit
 * - 2: Right bumper hit
 * - 3: Both bumpers hit
 */
extern int bump_side;

// ================================
//  Hazard Reporting Control
// ================================

/**
 * @brief Enable hazard detection reporting
 * 
 * Activates detailed reporting of hazards encountered during movement.
 * When enabled, hazard events may be logged or transmitted to connected systems.
 */
void enable_hazard_reporting(void);

/**
 * @brief Disable hazard detection reporting
 * 
 * Deactivates hazard reporting to reduce communication overhead
 * or when detailed hazard tracking is not needed.
 */
void disable_hazard_reporting(void);

/**
 * @brief Check if hazard reporting is currently enabled
 * 
 * @return true if hazard reporting is enabled, false otherwise
 */
bool is_hazard_reporting_enabled(void);

#endif
