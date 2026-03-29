/*
 * IMU.h
 *
 *  BNO055 IMU driver (I2C1 on PA6/PA7) for CyBOT
 *  Low-level I2C + high-level heading / cardinal helpers
 *
 *  Authors: Shawn and Shun
 *
 *  Description: Comprehensive driver for the BNO055 9-axis Inertial Measurement Unit (IMU).
 *               Provides both low-level I2C communication functions and high-level APIs for:
 *               - Reading Euler angles (heading, roll, pitch)
 *               - Reading linear acceleration, magnetometer, and gravity vector data
 *               - Compass heading with reference calibration
 *               - Cardinal direction detection (4-way and 8-way)
 *
 *               The BNO055 communicates via I2C1 on pins PA6 (SCL) and PA7 (SDA).
 *               Device address selection is controlled via PB7.
 */

#ifndef IMU_H_
#define IMU_H_

#include <stdint.h>
#include <stdbool.h>
#include "timer.h"
#include <inc/tm4c123gh6pm.h>

// ====== BNO055 I2C addresses ======
#define BNO055_ADDRESS_A  (0x28)
#define BNO055_ADDRESS_B  (0x29)

// ====== Page 0 register map (subset we use) ======
#define IMU_CHIP_ID         0x00
#define IMU_PAGE_ID         0x07
#define IMU_ACC_DATAX_LSB   0x08
#define IMU_ACC_DATAX_MSB   0x09
#define IMU_ACC_DATAY_LSB   0x0A
#define IMU_ACC_DATAY_MSB   0x0B
#define IMU_ACC_DATAZ_LSB   0x0C
#define IMU_ACC_DATAZ_MSB   0x0D
#define IMU_MAG_DATAX_LSB   0x0E
#define IMU_MAG_DATAX_MSB   0x0F
#define IMU_MAG_DATAY_LSB   0x10
#define IMU_MAG_DATAY_MSB   0x11
#define IMU_MAG_DATAZ_LSB   0x12
#define IMU_MAG_DATAZ_MSB   0x13
#define IMU_GYR_DATAX_LSB   0x14
#define IMU_GYR_DATAX_MSB   0x15
#define IMU_GYR_DATAY_LSB   0x16
#define IMU_GYR_DATAY_MSB   0x17
#define IMU_GYR_DATAZ_LSB   0x18
#define IMU_GYR_DATAZ_MSB   0x19
#define IMU_EUL_HEAD_LSB    0x1A
#define IMU_EUL_HEAD_MSB    0x1B
#define IMU_EUL_ROLL_LSB    0x1C
#define IMU_EUL_ROLL_MSB    0x1D
#define IMU_EUL_PTCH_LSB    0x1E
#define IMU_EUL_PTCH_MSB    0x1F
#define IMU_LIA_DATAX_LSB   0x28
#define IMU_LIA_DATAX_MSB   0x29
#define IMU_LIA_DATAY_LSB   0x2A
#define IMU_LIA_DATAY_MSB   0x2B
#define IMU_LIA_DATAZ_LSB   0x2C
#define IMU_LIA_DATAZ_MSB   0x2D
#define IMU_GRV_DATAX_LSB   0x2E
#define IMU_GRV_DATAX_MSB   0x2F
#define IMU_GRV_DATAY_LSB   0x30
#define IMU_GRV_DATAY_MSB   0x31
#define IMU_GRV_DATAZ_LSB   0x32
#define IMU_GRV_DATAZ_MSB   0x33
#define IMU_TEMP            0x34
#define IMU_CALIB_STAT      0x35
#define IMU_SYS_STATUS      0x39
#define IMU_UNIT_SEL        0x3B
#define IMU_OPR_MODE        0x3D

// ====== Low-level API (used inside IMU.c and for debugging) ======

/**
 * @brief Set the BNO055 I2C address via GPIO pin PB7
 * 
 * Controls the COM3 pin on the BNO055 to select between two possible I2C addresses.
 * 
 * @param addr I2C address to use (BNO055_ADDRESS_A = 0x28 or BNO055_ADDRESS_B = 0x29)
 */
void addr_set(uint8_t addr);

/**
 * @brief Initialize I2C1 peripheral
 * 
 * Configures I2C1 module on PA6 (SCL) and PA7 (SDA) for communication with the BNO055.
 * Sets up clock speed, GPIO alternate functions, and I2C master mode.
 */
void I2C1_Init(void);

/**
 * @brief Initialize BNO055 IMU sensor
 * 
 * Configures the BNO055 by setting operation mode and unit selections.
 * Should be called after I2C1_Init().
 */
void BNO055_Init(void);

/**
 * @brief Write data to BNO055 register(s) via I2C
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @param reg_addr Starting register address to write to
 * @param data Pointer to data buffer to write
 * @param len Number of bytes to write
 * @return 0 on success, negative on error
 */
int I2C1_Write(uint8_t device_addr, uint8_t reg_addr,
               const uint8_t *data, uint8_t len);

/**
 * @brief Read data from BNO055 register(s) via I2C
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @param reg_addr Starting register address to read from
 * @param data Pointer to buffer to store read data
 * @param len Number of bytes to read
 * @return 0 on success, negative on error
 */
int I2C1_Read(uint8_t device_addr, uint8_t reg_addr,
              uint8_t *data, uint8_t len);

/**
 * @brief Read raw Euler heading angle from BNO055
 * 
 * Heading (yaw) is the rotation around the Z-axis.
 * Raw value needs to be divided by 16 to get degrees (0-360°).
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit heading value (multiply by 1/16 for degrees)
 */
int16_t read_euler_heading(uint8_t device_addr);

/**
 * @brief Read raw Euler roll angle from BNO055
 * 
 * Roll is the rotation around the X-axis.
 * Raw value needs to be divided by 16 to get degrees (-180° to +180°).
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit roll value (multiply by 1/16 for degrees)
 */
int16_t read_euler_roll(uint8_t device_addr);

/**
 * @brief Read raw Euler pitch angle from BNO055
 * 
 * Pitch is the rotation around the Y-axis.
 * Raw value needs to be divided by 16 to get degrees (-90° to +90°).
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit pitch value (multiply by 1/16 for degrees)
 */
int16_t read_euler_pitch(uint8_t device_addr);

/**
 * @brief Read linear acceleration X-axis component
 * 
 * Linear acceleration with gravity removed. Unit: 1 m/s² = 100 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit X-axis linear acceleration (divide by 100 for m/s²)
 */
int16_t read_linear_acceleration_x(uint8_t device_addr);

/**
 * @brief Read linear acceleration Y-axis component
 * 
 * Linear acceleration with gravity removed. Unit: 1 m/s² = 100 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit Y-axis linear acceleration (divide by 100 for m/s²)
 */
int16_t read_linear_acceleration_y(uint8_t device_addr);

/**
 * @brief Read linear acceleration Z-axis component
 * 
 * Linear acceleration with gravity removed. Unit: 1 m/s² = 100 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit Z-axis linear acceleration (divide by 100 for m/s²)
 */
int16_t read_linear_acceleration_z(uint8_t device_addr);

/**
 * @brief Read magnetometer X-axis component
 * 
 * Magnetic field strength. Unit: 1 µT (microTesla) = 16 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit X-axis magnetic field value (divide by 16 for µT)
 */
int16_t read_mag_x(uint8_t device_addr);

/**
 * @brief Read magnetometer Y-axis component
 * 
 * Magnetic field strength. Unit: 1 µT (microTesla) = 16 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit Y-axis magnetic field value (divide by 16 for µT)
 */
int16_t read_mag_y(uint8_t device_addr);

/**
 * @brief Read magnetometer Z-axis component
 * 
 * Magnetic field strength. Unit: 1 µT (microTesla) = 16 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit Z-axis magnetic field value (divide by 16 for µT)
 */
int16_t read_mag_z(uint8_t device_addr);

/**
 * @brief Read gravity vector X-axis component
 * 
 * Gravity vector in m/s². Unit: 1 m/s² = 100 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit X-axis gravity vector (divide by 100 for m/s²)
 */
int16_t read_grav_vec_x(uint8_t device_addr);

/**
 * @brief Read gravity vector Y-axis component
 * 
 * Gravity vector in m/s². Unit: 1 m/s² = 100 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit Y-axis gravity vector (divide by 100 for m/s²)
 */
int16_t read_grav_vec_y(uint8_t device_addr);

/**
 * @brief Read gravity vector Z-axis component
 * 
 * Gravity vector in m/s². Unit: 1 m/s² = 100 LSB.
 * 
 * @param device_addr I2C device address (0x28 or 0x29)
 * @return Raw 16-bit Z-axis gravity vector (divide by 100 for m/s²)
 */
int16_t read_grav_vec_z(uint8_t device_addr);

// ================================
//  High-level heading / cardinals
// ================================

/**
 * @brief Initialize the IMU system (full initialization with calibration)
 * 
 * Performs complete IMU setup including:
 * - I2C1 peripheral initialization
 * - BNO055 sensor initialization
 * - Calibration wait time
 * 
 * Call this once at startup after timer_init(), lcd_init(), etc.
 * This function includes calibration waiting time.
 */
void imu_init(void);

/**
 * @brief Initialize I2C and BNO055 but skip calibration
 * 
 * Sets up the IMU hardware without waiting for calibration to complete.
 * Useful when you want to defer calibration until after establishing
 * communication (e.g., with a remote GUI).
 * 
 * Follow up with imu_calibrate() when ready.
 */
void imu_init_no_calibration(void);

/**
 * @brief Perform IMU calibration
 * 
 * Waits for the BNO055 to complete its calibration process.
 * Can be called separately after imu_init_no_calibration().
 * The sensor calibrates its magnetometer, accelerometer, and gyroscope.
 */
void imu_calibrate(void);

/**
 * @brief Set the current heading as the reference "North" direction
 * 
 * Captures the current IMU heading and uses it as the reference point (0°).
 * Call this once when the robot is facing your chosen "North" direction.
 * After calling this, imu_get_heading_deg() returns 0 when facing this direction.
 * 
 * This allows for relative heading measurements independent of magnetic north.
 */
void imu_set_reference_heading(void);

/**
 * @brief Get current heading in degrees relative to reference
 * 
 * Returns the heading angle relative to the reference set by
 * imu_set_reference_heading().
 * 
 * @return Heading in degrees (0-360°), where 0° is the reference direction,
 *         90° is 90° clockwise from reference, etc.
 */
float imu_get_heading_deg(void);

/**
 * @brief Get current heading as a 4-way cardinal direction
 * 
 * Converts the current heading to one of four cardinal directions:
 * - "N" (North): 315° to 45°
 * - "E" (East): 45° to 135°
 * - "S" (South): 135° to 225°
 * - "W" (West): 225° to 315°
 * 
 * @return Pointer to string constant containing "N", "E", "S", or "W"
 */
const char *imu_get_cardinal_4(void);

/**
 * @brief Get current heading as an 8-way cardinal direction
 * 
 * Converts the current heading to one of eight cardinal/intercardinal directions:
 * - "N" (North): 337.5° to 22.5°
 * - "NE" (Northeast): 22.5° to 67.5°
 * - "E" (East): 67.5° to 112.5°
 * - "SE" (Southeast): 112.5° to 157.5°
 * - "S" (South): 157.5° to 202.5°
 * - "SW" (Southwest): 202.5° to 247.5°
 * - "W" (West): 247.5° to 292.5°
 * - "NW" (Northwest): 292.5° to 337.5°
 * 
 * @return Pointer to string constant containing cardinal/intercardinal direction
 */
const char *imu_get_cardinal_8(void);

#endif /* IMU_H_ */