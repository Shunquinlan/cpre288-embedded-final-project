/**
 * Adrian's GUI-Enabled CyBot Program
 * 
 * Complete WiFi socket server that works with the Python GUI
 * Uses UART1 for WiFi-to-UART bridge communication
 * Integrates movement, cliff detection, servo control, and scanning
 * 
 * Commands: w (forward), a (left), s (backward), d (right), t (stop)
 * Enhanced with servo commands and advanced scanning capabilities
 * Sends "OK" response after each command so GUI doesn't timeout
 * 
 * This is the MAIN file for the project
 */

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include "../inc/timer.h"
#include "../inc/lcd.h" 
#include "../inc/open_interface.h"
#include "../inc/movement.h"
#include "../inc/cliff.h"
#include "../inc/uart.h"
#include "../inc/servo.h"
#include "../inc/scan.h"
#include "../inc/adc.h"
#include "../inc/ping.h"
#include "../inc/sound.h"
#include "../inc/led.h"
#include "../inc/imu.h"
#include "../inc/ldr.h"
#include "../inc/remote.h"
#include <string.h>
#include <stdio.h>

// Global variables required by uart.c
volatile char uart_data;
volatile char flag;

int main(void) {
    // Initialize all systems
    timer_init();
    lcd_init();
    uart_init(); // Initialize UART1 for GUI communication
    servo_init(); // Initialize servo control
    adc_init();   // Initialize ADC for IR sensor
    ldr_init(); // Initialize LDR for tape detection
    ping_init();  // Initialize ping sensors
    ir_recv_init();  // Initialize IR receiver  

    lcd_printf("Adrian's CyBot\nGUI Ready!");
    
    // Initialize movement system
    oi_t *sensor_data = oi_alloc();
    oi_init(sensor_data);
    
    // Initialize sound system
    sound_init();
    
    // Initialize IMU/compass (without calibration - will calibrate after connection)
    lcd_printf("Initializing\nIMU/Compass...");
    uart_sendStr("SYSTEM_INIT: Initializing IMU hardware\r\n");
    imu_init_no_calibration();   // Does I2C init and BNO055 config, but skips calibration
    lcd_printf("IMU Ready!\nWaiting for GUI");
    timer_waitMillis(500);
    
    char my_data;
    char command[50];
    int index = 0;
    
    // Startup message
    lcd_printf("Adrian's GUI\nServer Ready & Loading!");
    // timer_waitMillis(2000);
    
    // Show ready status
    lcd_printf("Ready for\nGUI commands");
    
    while(1) {
        // Get first byte - wait until client sends data
        index = 0;
        do {
            my_data = uart_receive();
        } while(my_data == 0); // Wait until we actually get data
        
        // Process the first byte and get rest of command
        while(my_data != '\n') {
            command[index] = my_data;
            index++;
            do {
                my_data = uart_receive();
            } while(my_data == 0); // Wait for each subsequent byte
        }
        
        command[index] = '\n';
        command[index+1] = 0;
        
        // Process command
        char cmd = command[0];
        
        // Check for old scan command (keep for compatibility)
        if(strncmp(command, "scan", 4) == 0) {
            object_detect_command();
            uart_sendStr("OK\r\n");
            timer_waitMillis(500);
            lcd_printf("GUI Ready\nSend Command");
            continue;
        }
        
        // Show what command we received
        lcd_printf("GUI CMD: %c\nProcessing...", cmd);
        
        switch(cmd) {
            // === SCANNING COMMANDS (matching scan.h) ===
            case 'b': // Basic scan (0-180 degrees)
                basic_scan_command();
                break;
                
            case 'o': // Object detection scan with tape detection
                object_detect_command();
                break;
                
            case 'k': // Tape detection with angle (format: k90, k120, etc.)
                {
                    int angle = 90; // default angle
                    // Parse angle from command string starting at position 1
                    if (index > 1) { // If we have more than just 'k'
                        // Convert the numeric part to integer
                        char angle_str[10] = {0}; // Initialize with zeros
                        int i = 0;
                        int j = 1; // Start after 'k'
                        
                        // Copy digits from command to angle_str
                        while (j < index && command[j] != '\n' && i < 9) {
                            if (command[j] >= '0' && command[j] <= '9') {
                                angle_str[i] = command[j];
                                i++;
                            }
                            j++;
                        }
                        
                        if (i > 0) { // If we found some digits
                            angle = atoi(angle_str);
                            // Validate angle range
                            if (angle < 0 || angle > 180) {
                                angle = 90; // Reset to default if invalid
                                uart_sendStr("TAPE: Invalid angle, using 90°\r\n");
                            }
                        }
                    }
                    
                    char tape_start_msg[50];
                    sprintf(tape_start_msg, "TAPE: Checking at %d degrees\r\n", angle);
                    uart_sendStr(tape_start_msg);
                    
                    tape_detect_command(angle);
                }
                break;
                
            // === COMPASS COMMANDS ===
            case 'C': // Calibrate IMU (uppercase C)
                lcd_printf("Calibrating\nIMU...");
                uart_sendStr("COMPASS: Starting IMU calibration\r\n");
                imu_calibrate();
                lcd_printf("IMU Ready!\nCalibrated");
                uart_sendStr("COMPASS: IMU calibration complete\r\n");
                break;
                
            case 'n': // Set IMU North reference
                imu_set_reference_heading();
                uart_sendStr("COMPASS: North reference set to current heading\r\n");
                lcd_printf("IMU North\nReference Set");
                break;
            
            case 'g': // Get compass heading (silent - no OK response)
                {
                    float heading = imu_get_heading_deg();
                    const char *cardinal = imu_get_cardinal_8();
                    
                    // Read calibration status
                    uint8_t cal_status = 0;
                    I2C1_Read(BNO055_ADDRESS_B, IMU_CALIB_STAT, &cal_status, 1);
                    uint8_t sys_cal = (cal_status >> 6) & 0x03;
                    uint8_t mag_cal = cal_status & 0x03;
                    
                    // Send compass data in format: "COMPASS: 123.4 NE CAL:3,2"
                    char compass_msg[64];
                    sprintf(compass_msg, "COMPASS: %.1f %s CAL:%d,%d\r\n", 
                            heading, cardinal, sys_cal, mag_cal);
                    uart_sendStr(compass_msg);
                    
                    // Skip the universal OK response at the end
                    lcd_printf("GUI Ready\nSend Command");
                    continue; // Skip to next iteration, bypassing the OK
                }
                break;
                
            // === SOUND COMMANDS ===
            case 'K': // Play OK beep (uppercase K to avoid conflict with tape detect)
                sound_play_ok();
                uart_sendStr("SOUND: OK beep\r\n");
                break;
                
            case 'N': // Play Error beep (uppercase N)
                sound_play_error();
                uart_sendStr("SOUND: Error beep\r\n");
                break;
                
            case 'F': // Play Soldier Found alarm (uppercase F)
                sound_play_soldier_found();
                uart_sendStr("SOUND: Soldier Found alarm\r\n");
                break;
                
            // === MOVEMENT COMMANDS ===
            case 'w': // Forward with cliff detection
                {
                    uart_sendStr("MOVE: Forward 10cm - starting\r\n");
                    int result = move_forward_safe(sensor_data, 10);
                    
                    // Calculate actual distance traveled in cm
                    float actual_distance_cm = actual_distance_traveled_mm / 10.0f;
                    
                    if (result == 1) {
                        // Bump detected - use bump_side global variable to determine which side
                        char *bumper_side;
                        if (bump_side == 1) {
                            bumper_side = "LEFT_BUMPER";
                        } else if (bump_side == 2) {
                            bumper_side = "RIGHT_BUMPER"; 
                        } else if (bump_side == 3) {
                            bumper_side = "BOTH_BUMPERS";
                        } else {
                            bumper_side = "UNKNOWN_BUMPER";
                        }
                        
                        // Only send legacy hazard message if hazard reporting is enabled
                        if (is_hazard_reporting_enabled()) {
                            char bump_msg[100];
                            sprintf(bump_msg, "HAZARD: %s detected - stopped after %.1f cm\r\n", 
                                    bumper_side, actual_distance_cm);
                            uart_sendStr(bump_msg);
                        }
                        lcd_printf("%s!\n%.1f cm", bumper_side, actual_distance_cm);
                    } else if (result == 2) {
                        // Border/edge detected (white tape)
                        if (is_hazard_reporting_enabled()) {
                            char border_msg[100];
                            sprintf(border_msg, "HAZARD: BORDER/WHITE_TAPE detected - stopped after %.1f cm\r\n", 
                                    actual_distance_cm);
                            uart_sendStr(border_msg);
                        }
                        lcd_printf("BORDER/TAPE!\n%.1f cm", actual_distance_cm);
                    } else if (result == 3) {
                        // Hole/cliff detected (black tape/drop-off)
                        if (is_hazard_reporting_enabled()) {
                            char hole_msg[100];
                            sprintf(hole_msg, "HAZARD: HOLE/CLIFF detected - stopped after %.1f cm\r\n", 
                                    actual_distance_cm);
                            uart_sendStr(hole_msg);
                        }
                        lcd_printf("HOLE/CLIFF!\n%.1f cm", actual_distance_cm);
                    } else {
                        // Success
                        char success_msg[100];
                        sprintf(success_msg, "MOVE: Forward completed successfully - traveled %.1f cm\r\n", 
                                actual_distance_cm);
                        uart_sendStr(success_msg);
                        lcd_printf("Move OK!\n%.1f cm done", actual_distance_cm);
                    }
                }
                break;
                
            case 'L': // Single LDR + IR sample & classification
                {
                    // Existing IR reading from your adc.c
                    uint16_t ir_raw = adc_read();      // assumes this exists
                    uint16_t ldr_raw = ldr_read_raw();

                    uint8_t cls = ldr_detect_surface();
                    const char *cls_str = ldr_get_surface_name(cls);

                    char msg[120];
                    sprintf(msg,
                            "LDR_CHECK: IR=%u, LDR=%u -> %s\r\n",
                            ir_raw, ldr_raw, cls_str);
                    uart_sendStr(msg);

                    // Quick feedback on LCD too
                    lcd_printf("IR=%u\nLDR=%u %s", ir_raw, ldr_raw, cls_str);
                }
                break;
    
                
            case 'f': // Custom forward distance (format: "f:distance")
                {
                    // Parse distance from command string (format: "f:50")
                    int custom_distance = 10; // default
                    if (command[1] == ':') {
                        // Parse integer after the colon
                        sscanf(&command[2], "%d", &custom_distance);
                        
                        // Clamp to reasonable range (1-200 cm)
                        if (custom_distance < 1) custom_distance = 1;
                        if (custom_distance > 200) custom_distance = 200;
                        
                        lcd_printf("Custom Fwd\n%d cm", custom_distance);
                    }
                    
                    char custom_start_msg[50];
                    sprintf(custom_start_msg, "MOVE: Custom forward %dcm - starting\r\n", custom_distance);
                    uart_sendStr(custom_start_msg);
                    
                    int result = move_forward_safe(sensor_data, custom_distance);
                    
                    // Calculate actual distance traveled in cm
                    float actual_distance_cm = actual_distance_traveled_mm / 10.0f;
                    
                    if (result >= 1 && result <= 3) {
                        // Bump detected - report which bumper and distance traveled
                        char *bumper_side;
                        if (result == 1) {
                            bumper_side = "LEFT_BUMPER";
                        } else if (result == 2) {
                            bumper_side = "RIGHT_BUMPER"; 
                        } else {
                            bumper_side = "CENTER_BUMPER"; // Both left and right triggered = center impact
                        }
                        
                        // Only send legacy hazard message if hazard reporting is enabled
                        if (is_hazard_reporting_enabled()) {
                            char bump_msg[100];
                            sprintf(bump_msg, "HAZARD: %s detected - stopped after %.1f cm\r\n", 
                                    bumper_side, actual_distance_cm);
                            uart_sendStr(bump_msg);
                        }
                        lcd_printf("%s!\n%.1f cm", bumper_side, actual_distance_cm);
                    } else if (result == 4) {
                        // Border/tape detected (high IR values > 2600)
                        if (is_hazard_reporting_enabled()) {
                            char border_msg[100];
                            sprintf(border_msg, "HAZARD: BORDER/WHITE_TAPE detected - stopped after %.1f cm\r\n", 
                                    actual_distance_cm);
                            uart_sendStr(border_msg);
                        }
                        lcd_printf("BORDER/TAPE!\n%.1f cm", actual_distance_cm);
                    } else if (result == 5) {
                        // Hole/cliff detected (low IR values < 2000)
                        if (is_hazard_reporting_enabled()) {
                            char hole_msg[100];
                            sprintf(hole_msg, "HAZARD: HOLE/CLIFF/EDGE detected - stopped after %.1f cm\r\n", 
                                    actual_distance_cm);
                            uart_sendStr(hole_msg);
                        }
                        lcd_printf("HOLE/CLIFF!\n%.1f cm", actual_distance_cm);
                    } else {
                        // Success
                        char success_msg[100];
                        sprintf(success_msg, "MOVE: Custom forward completed successfully - traveled %.1f cm\r\n", 
                                actual_distance_cm);
                        uart_sendStr(success_msg);
                        lcd_printf("Custom OK!\n%.1f cm done", actual_distance_cm);
                    }
                }
                break;
                
            case 'm': // Custom movement distance (format: "m35")
                {
                    int custom_distance = 10; // default
                    // Parse distance from command string starting at position 1
                    if (index > 1) { // If we have more than just 'm'
                        // Convert the numeric part to integer
                        char distance_str[10] = {0}; // Initialize with zeros
                        int i = 0;
                        int j = 1; // Start after 'm'
                        
                        // Copy digits from command to distance_str
                        while (j < index && command[j] != '\n' && i < 9) {
                            if (command[j] >= '0' && command[j] <= '9') {
                                distance_str[i] = command[j];
                                i++;
                            }
                            j++;
                        }
                        
                        if (i > 0) { // If we found some digits
                            custom_distance = atoi(distance_str);
                            // Validate distance range
                            if (custom_distance < 1 || custom_distance > 200) {
                                custom_distance = 10; // Reset to default if invalid
                                uart_sendStr("MOVE: Invalid distance, using 10cm\r\n");
                            }
                        }
                    }
                    
                    char move_start_msg[50];
                    sprintf(move_start_msg, "MOVE: Moving %d cm forward\r\n", custom_distance);
                    uart_sendStr(move_start_msg);
                    lcd_printf("Custom Move\n%d cm", custom_distance);
                    
                    int result = move_forward_safe(sensor_data, custom_distance);
                    
                    // Calculate actual distance traveled in cm
                    float actual_distance_cm = actual_distance_traveled_mm / 10.0f;
                    
                    if (result >= 1 && result <= 3) {
                        // Bump detected - report which bumper and distance traveled
                        char *bumper_side;
                        if (result == 1) {
                            bumper_side = "LEFT_BUMPER";
                        } else if (result == 2) {
                            bumper_side = "RIGHT_BUMPER"; 
                        } else {
                            bumper_side = "CENTER_BUMPER"; // Both left and right triggered = center impact
                        }
                        
                        // Only send legacy hazard message if hazard reporting is enabled
                        if (is_hazard_reporting_enabled()) {
                            char bump_msg[100];
                            sprintf(bump_msg, "HAZARD: %s detected - stopped after %.1f cm\r\n", 
                                    bumper_side, actual_distance_cm);
                            uart_sendStr(bump_msg);
                        }
                        lcd_printf("%s!\n%.1f cm", bumper_side, actual_distance_cm);
                    } else if (result == 4) {
                        // Border/tape detected (high IR values > 2600)
                        if (is_hazard_reporting_enabled()) {
                            char border_msg[100];
                            sprintf(border_msg, "HAZARD: BORDER/WHITE_TAPE detected - stopped after %.1f cm\r\n", 
                                    actual_distance_cm);
                            uart_sendStr(border_msg);
                        }
                        lcd_printf("BORDER/TAPE!\n%.1f cm", actual_distance_cm);
                    } else if (result == 5) {
                        // Hole/cliff detected (low IR values < 2000)
                        if (is_hazard_reporting_enabled()) {
                            char hole_msg[100];
                            sprintf(hole_msg, "HAZARD: HOLE/CLIFF/EDGE detected - stopped after %.1f cm\r\n", 
                                    actual_distance_cm);
                            uart_sendStr(hole_msg);
                        }
                        lcd_printf("HOLE/CLIFF!\n%.1f cm", actual_distance_cm);
                    } else {
                        // Success
                        char success_msg[100];
                        sprintf(success_msg, "MOVE: Custom movement completed successfully - traveled %.1f cm\r\n", 
                                actual_distance_cm);
                        uart_sendStr(success_msg);
                        lcd_printf("Move OK!\n%.1f cm done", actual_distance_cm);
                    }
                }
                break;
                
            case 's': // Backward
                uart_sendStr("MOVE: Backward 10cm - starting\r\n");
                safe_move_backward(sensor_data, 10);
                uart_sendStr("MOVE: Backward completed\r\n");
                break;
                
            case 'a': // Left turn
                uart_sendStr("MOVE: Left turn 30° - starting\r\n");
                turn_left(sensor_data, 30);
                uart_sendStr("MOVE: Left turn completed\r\n");
                break;
                
            case 'd': // Right turn  
                uart_sendStr("MOVE: Right turn 30° - starting\r\n");
                turn_right(sensor_data, 30);
                uart_sendStr("MOVE: Right turn completed\r\n");
                break;
                
            case 't': // Stop
                oi_setWheels(0, 0);
                break;
                
            // === EXIT MODE COMMANDS ===
            case 'e': // Manual exit step (move_forward_exit)
                {
                    uart_sendStr("EXIT: Manual exit step - ignoring white borders\r\n");
                    lcd_printf("Manual Exit\n10 cm step");
                    
                    int exit_result = move_forward_exit(sensor_data, 10);
                    
                    if (exit_result == 1) {
                        // Bump detected
                        uart_sendStr("EXIT: Bump detected during manual exit\r\n");
                        lcd_printf("Exit Bump!\nStopped");
                    } else if (exit_result == 2) {
                        // Cliff/hole detected
                        uart_sendStr("EXIT: Cliff/hole detected during manual exit\r\n");
                        lcd_printf("Exit Cliff!\nStopped");
                    } else {
                        // Success
                        uart_sendStr("EXIT: Manual step completed\r\n");
                        lcd_printf("Exit Step\nComplete");
                    }
                }
                break;
                
            case 'x': // Auto exit field (auto_exit_field)
                {
                    uart_sendStr("EXIT: Starting automatic field exit\r\n");
                    lcd_printf("Auto Exit\nStarting...");
                    
                    int auto_result = auto_exit_field(sensor_data);
                    
                    if (auto_result == 0) {
                        // Success - completed full exit
                        uart_sendStr("EXIT: Auto exit completed successfully - soldier down!\r\n");
                        lcd_printf("Exit Success!\nSoldier Down");
                    } else if (auto_result == -1) {
                        // Failed - distance limit reached
                        uart_sendStr("EXIT: Auto exit failed - distance limit\r\n");
                        lcd_printf("Exit Failed\nDist Limit");
                    } else if (auto_result == -2) {
                        // Halted by user
                        uart_sendStr("EXIT: Auto exit halted by user\r\n");
                        lcd_printf("Exit Halted\nBy User");
                    }
                }
                break;
                
            case 'z': // Halt command (used to stop auto exit)
                oi_setWheels(0, 0);
                uart_sendStr("HALT: Robot stopped\r\n");
                lcd_printf("Halted\nStopped");
                break;
                
            case 'h': // Help - show available commands
                uart_sendStr("ADRIAN'S CYBOT COMMANDS:\r\n");
                uart_sendStr("=== SCANNING (scan.h functions) ===\r\n");
                uart_sendStr("p=point_scan (90deg), b=basic_scan (0-180)\r\n");
                uart_sendStr("o=object_detect (with tape detection)\r\n");
                uart_sendStr("k=tape_detect (check for tape @90deg)\r\n");
                uart_sendStr("=== COMPASS/IMU ===\r\n");
                uart_sendStr("n=set IMU North reference to current heading\r\n");
                uart_sendStr("=== SOUND ===\r\n");
                uart_sendStr("K=play OK beep, N=play Error beep, F=play Soldier Found alarm\r\n");
                uart_sendStr("=== MOVEMENT (with hazard detection) ===\r\n");
                uart_sendStr("w=forward (10cm), f:N=custom forward (N cm)\r\n");
                uart_sendStr("m=custom move (mN format), s=backward (10cm)\r\n");
                uart_sendStr("a=left (30deg), d=right (30deg), t=stop\r\n");
                uart_sendStr("=== EXIT MODE (ignores white borders) ===\r\n");
                uart_sendStr("e=manual exit step (10cm incremental)\r\n");
                uart_sendStr("x=auto exit field (automatic 2-border crossing)\r\n");
                uart_sendStr("z=halt auto exit (return to manual control)\r\n");
                uart_sendStr("=== HAZARD DETECTION ===\r\n");
                uart_sendStr("BUMPERS: LEFT_BUMPER, RIGHT_BUMPER, CENTER_BUMPER\r\n");
                uart_sendStr("CLIFF: BORDER/WHITE_TAPE (>2600) vs HOLE/CLIFF/EDGE (<2000)\r\n");
                uart_sendStr("=== OTHER ===\r\n");
                uart_sendStr("h=help\r\n");
                break;
                
            default:
                uart_sendStr("UNKNOWN_COMMAND\r\n");
                break;
        }
        
        // CRITICAL: Send response so GUI doesn't timeout
        uart_sendStr("OK\r\n");
        
        // Show completion status
        lcd_printf("GUI CMD: %c\nComplete!", cmd);
        
        // Brief delay then ready for next command
        timer_waitMillis(500);
        lcd_printf("GUI Ready\nSend Command");
    }
    
    oi_free(sensor_data);
    return 0;
}
