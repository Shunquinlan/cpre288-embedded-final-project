/*
 * IMU.c
 *
 *  BNO055 IMU driver (I2C1 on PA6/PA7) for CyBOT
 *
 *  Authors: Shawn and Shun (+ tweaks for hard-reset & timeouts)
 */

#include "../inc/imu.h"
#include "../inc/tm4c123gh6pm.h"
#include "../inc/timer.h"
#include "../inc/lcd.h"
#include "../inc/uart.h"
#include <math.h>
#include <stdio.h>
#include <stdint.h>

// ========================================
//  Address select helper (uses PB7)
// ========================================
void addr_set(uint8_t addr)
{
    // On the CyBOT board PB7 is tied to the BNO055 ADR pin.
    // 0x28 => ADR low,  0x29 => ADR high.
    switch (addr)
    {
    case BNO055_ADDRESS_A:  // 0x28
        GPIO_PORTB_DATA_R &= ~0x80;
        break;
    case BNO055_ADDRESS_B:  // 0x29
    default:
        GPIO_PORTB_DATA_R |= 0x80;
        break;
    }
}

// ========================================
//  Hard reset helper (PB6 is reset line)
// ========================================
static void imu_hard_reset(void)
{
    // PB6 is the reset line: LOW = reset, HIGH = run
    GPIO_PORTB_DATA_R &= ~0x40;   // drive PB6 low
    timer_waitMillis(10);         // hold reset for a bit
    GPIO_PORTB_DATA_R |= 0x40;    // release reset (high)
    timer_waitMillis(650);        // wait for BNO055 boot
}

// ========================================
//  I2C1 init (PA6 = SCL, PA7 = SDA)
// ========================================
void I2C1_Init(void)
{
    // Enable clocks for I2C1 and GPIOA/GPIOB
    SYSCTL_RCGCI2C_R |= 0x02;  // I2C1
    SYSCTL_RCGCGPIO_R |= 0x03; // Port A + Port B

    while ((SYSCTL_PRI2C_R & 0x02) == 0) {}
    while ((SYSCTL_PRGPIO_R & 0x03) == 0) {}

    // Configure PA6 (SCL) & PA7 (SDA) for I2C
    GPIO_PORTA_DIR_R   |= 0xC0;              // PA6, PA7 outputs (I2C controls dir)
    GPIO_PORTA_AFSEL_R |= 0xC0;              // alternate function
    GPIO_PORTA_ODR_R   |= 0x80;              // SDA open-drain
    GPIO_PORTA_DEN_R   |= 0xC0;              // digital enable
    GPIO_PORTA_PCTL_R   = (GPIO_PORTA_PCTL_R & 0x00FFFFFF) | 0x33000000;

    // Configure PB2, PB6, PB7 as digital; PB6/PB7 outputs
    GPIO_PORTB_DEN_R   |= 0xC4;              // PB2, PB6, PB7
    GPIO_PORTB_AFSEL_R &= ~0xC0;             // PB6/PB7 as GPIO
    GPIO_PORTB_DIR_R    = (GPIO_PORTB_DIR_R & ~0x04) | 0xC0; // PB6,PB7 out

    // I2C1 master, 100 kHz
    I2C1_MCR_R  = 0x10;   // master
    I2C1_MTPR_R = 0x07;   // ~100 kHz @ 16 MHz

    // PB6 = reset line – keep it high initially
    GPIO_PORTB_DATA_R |= 0x40;

    // Select BNO055 address B by default
    addr_set(BNO055_ADDRESS_B);
}

// ========================================
//  Low-level write & read (with timeouts)
// ========================================

static int i2c_wait_while_busy(void)
{
    int timeout = 100000;
    while ((I2C1_MCS_R & 0x01) && --timeout) {}
    return (timeout == 0) ? -1 : 0;
}

// Write 'len' bytes starting at reg_addr.
// For this lab, we really only ever pass len=1.
int I2C1_Write(uint8_t device_addr, uint8_t reg_addr,
               const uint8_t *data, uint8_t len)
{
    uint8_t i;

    if (len == 0) return -1;

    // Send register address
    I2C1_MSA_R = (device_addr << 1) | 0;   // write
    I2C1_MDR_R = reg_addr;
    I2C1_MCS_R = 0x03;                     // START + RUN
    if (i2c_wait_while_busy() < 0) {
        uart_sendStr("IMU_ERROR: I2C timeout (write addr)\r\n");
        return -2;
    }

    // Write each data byte
    for (i = 0; i < len; i++)
    {
        I2C1_MDR_R = data[i];
        I2C1_MCS_R = (i == len - 1) ? 0x05 : 0x01;  // RUN (+STOP for last)
        if (i2c_wait_while_busy() < 0) {
            uart_sendStr("IMU_ERROR: I2C timeout (write data)\r\n");
            return -3;
        }
    }

    return 0;
}

// Read 'len' bytes starting at reg_addr.
// In this code we always call with len==1, so implement that cleanly.
int I2C1_Read(uint8_t device_addr, uint8_t reg_addr,
              uint8_t *data, uint8_t len)
{
    if (len == 0) return -1;
    if (len > 1)  return -2; // multi-byte read not implemented here

    // Write register address
    I2C1_MSA_R = (device_addr << 1) | 0;   // write
    I2C1_MDR_R = reg_addr;
    I2C1_MCS_R = 0x03;                     // START + RUN
    if (i2c_wait_while_busy() < 0) {
        uart_sendStr("IMU_ERROR: I2C timeout (read addr)\r\n");
        return -3;
    }

    // Re-start as read, one byte, STOP
    I2C1_MSA_R = (device_addr << 1) | 1;   // read
    I2C1_MCS_R = 0x07;                     // START + RUN + STOP
    if (i2c_wait_while_busy() < 0) {
        uart_sendStr("IMU_ERROR: I2C timeout (read data)\r\n");
        return -4;
    }

    *data = (uint8_t)I2C1_MDR_R;
    return 0;
}

// ========================================
//  BNO055 configuration (without calibration)
// ========================================
static void BNO055_Config(void)
{
    // Per datasheet, wait for chip to boot
    timer_waitMillis(650);

    // Make sure we're talking to a BNO055
    uint8_t id = 0;
    I2C1_Read(BNO055_ADDRESS_B, IMU_CHIP_ID, &id, 1);
    if (id != 0xA0)
    {
        lcd_printf("IMU ID? 0x%02X", id);
        uart_sendStr("IMU_ERROR: Invalid chip ID\r\n");
        timer_waitMillis(1000);
    }

    // CONFIGMODE before touching config registers
    uint8_t config_mode = 0x00;   // CONFIGMODE
    I2C1_Write(BNO055_ADDRESS_B, IMU_OPR_MODE, &config_mode, 1);
    timer_waitMillis(25);

    // Page 0
    uint8_t page0 = 0x00;
    I2C1_Write(BNO055_ADDRESS_B, IMU_PAGE_ID, &page0, 1);
    timer_waitMillis(10);

    // Units: degrees for Euler angles
    uint8_t unitsel = 0x00;
    I2C1_Write(BNO055_ADDRESS_B, IMU_UNIT_SEL, &unitsel, 1);
    timer_waitMillis(10);

    // Axis remap + sign for CyBOT mounting (P0)
    uint8_t axis_config      = 0x21;
    uint8_t axis_sign_config = 0x04;
    I2C1_Write(BNO055_ADDRESS_B, 0x41, &axis_config, 1);
    timer_waitMillis(10);
    I2C1_Write(BNO055_ADDRESS_B, 0x42, &axis_sign_config, 1);
    timer_waitMillis(10);

    // NDOF fusion mode
    uint8_t ndof_mode = 0x0C;
    I2C1_Write(BNO055_ADDRESS_B, IMU_OPR_MODE, &ndof_mode, 1);
    timer_waitMillis(650);
    
    uart_sendStr("IMU_CONFIG_COMPLETE\r\n");
}

// ========================================
//  BNO055 calibration (separate function)
// ========================================
void imu_calibrate(void)
{
    uint8_t cal_status = 0;
    uint8_t sys_cal = 0, gyro_cal = 0, accel_cal = 0, mag_cal = 0;

    lcd_printf("Calibrating...\n");
    uart_sendStr("IMU_CALIBRATION_START\r\n");
    
    // Wait until SYS, GYRO, and MAG are fully calibrated
    while (sys_cal != 3 || gyro_cal != 3 || mag_cal != 3)
    {
        I2C1_Read(BNO055_ADDRESS_B, IMU_CALIB_STAT, &cal_status, 1);

        sys_cal   = (cal_status >> 6) & 0x03;
        gyro_cal  = (cal_status >> 4) & 0x03;
        accel_cal = (cal_status >> 2) & 0x03;
        mag_cal   =  cal_status       & 0x03;

        lcd_printf("Calibrating...\nS:%d G:%d A:%d M:%d",
                   sys_cal, gyro_cal, accel_cal, mag_cal);
        
        // Send calibration status to UART log
        char log_buffer[64];
        sprintf(log_buffer, "IMU_CALIB: SYS=%d GYRO=%d ACCEL=%d MAG=%d\r\n",
                sys_cal, gyro_cal, accel_cal, mag_cal);
        uart_sendStr(log_buffer);

        timer_waitMillis(500);
    }

    lcd_printf("Calib done\nS:%d G:%d A:%d M:%d",
               sys_cal, gyro_cal, accel_cal, mag_cal);
    uart_sendStr("IMU_CALIBRATION_COMPLETE: SYS=3 GYRO=3 ACCEL=3 MAG=3\r\n");
    timer_waitMillis(800);
}

// Legacy function for backward compatibility
void BNO055_Init(void)
{
    BNO055_Config();
    imu_calibrate();
}

// ========================================
//  Data helpers (accel/mag/grav/Euler)
// ========================================
static int16_t read_16_pair(uint8_t addr_lsb)
{
    uint8_t data[2];
    I2C1_Read(BNO055_ADDRESS_B, addr_lsb,     &data[0], 1);
    timer_waitMillis(1);
    I2C1_Read(BNO055_ADDRESS_B, addr_lsb + 1, &data[1], 1);
    return (int16_t)((data[1] << 8) | data[0]);
}

// Linear Acceleration
int16_t read_linear_acceleration_x(uint8_t device_addr)
{
    (void)device_addr; // we always use BNO055_ADDRESS_B
    return read_16_pair(IMU_LIA_DATAX_LSB);
}
int16_t read_linear_acceleration_y(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_LIA_DATAY_LSB);
}
int16_t read_linear_acceleration_z(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_LIA_DATAZ_LSB);
}

// Magnetometer
int16_t read_mag_x(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_MAG_DATAX_LSB);
}
int16_t read_mag_y(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_MAG_DATAY_LSB);
}
int16_t read_mag_z(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_MAG_DATAZ_LSB);
}

// Gravity vector
int16_t read_grav_vec_x(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_GRV_DATAX_LSB);
}
int16_t read_grav_vec_y(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_GRV_DATAY_LSB);
}
int16_t read_grav_vec_z(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_GRV_DATAZ_LSB);
}

// Euler angles
int16_t read_euler_heading(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_EUL_HEAD_LSB);
}
int16_t read_euler_roll(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_EUL_ROLL_LSB);
}
int16_t read_euler_pitch(uint8_t device_addr)
{
    (void)device_addr;
    return read_16_pair(IMU_EUL_PTCH_LSB);
}

// ========================================
//  High-level heading / cardinal helpers
// ========================================
static float heading_offset_deg = 0.0f; // reference "North"

// Internal: raw heading in degrees, sensor frame [0,360)
static float imu_get_heading_deg_raw(void)
{
    int16_t raw = read_euler_heading(BNO055_ADDRESS_B);

    // BNO055 Euler: 16 LSB per degree (when in degrees mode)
    float deg = (float)raw / 16.0f;

    while (deg < 0.0f)    deg += 360.0f;
    while (deg >= 360.0f) deg -= 360.0f;

    return deg;
}

// Call once at startup
void imu_init(void)
{
    I2C1_Init();
    imu_hard_reset();  // force BNO055 reboot each time
    BNO055_Init();     // config + calibration
    timer_waitMillis(50);
}

// Initialize without calibration (for delayed calibration after connection)
void imu_init_no_calibration(void)
{
    I2C1_Init();
    imu_hard_reset();
    BNO055_Config();  // Only config, no calibration
    timer_waitMillis(50);
    uart_sendStr("IMU_INIT_NO_CALIB: Ready for calibration command\r\n");
}

// Call when robot is facing our chosen "North"
void imu_set_reference_heading(void)
{
    float raw = imu_get_heading_deg_raw();
    heading_offset_deg = raw;
}

// Heading relative to reference, in degrees [0,360)
float imu_get_heading_deg(void)
{
    float h = imu_get_heading_deg_raw() - heading_offset_deg;

    while (h < 0.0f)    h += 360.0f;
    while (h >= 360.0f) h -= 360.0f;

    return h;
}

// 4-way compass: N / E / S / W
const char *imu_get_cardinal_4(void)
{
    float h = imu_get_heading_deg();

    if (h < 45.0f || h >= 315.0f)  return "N";
    else if (h < 135.0f)           return "E";
    else if (h < 225.0f)           return "S";
    else                           return "W";
}

// 8-way compass: N / NE / E / SE / S / SW / W / NW
const char *imu_get_cardinal_8(void)
{
    float h = imu_get_heading_deg();

    if      (h < 22.5f || h >= 337.5f) return "N";
    else if (h < 67.5f)                return "NE";
    else if (h < 112.5f)               return "E";
    else if (h < 157.5f)               return "SE";
    else if (h < 202.5f)               return "S";
    else if (h < 247.5f)               return "SW";
    else if (h < 292.5f)               return "W";
    else                               return "NW";
}
