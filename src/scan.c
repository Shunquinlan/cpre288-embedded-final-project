#include "../inc/scan.h"
#include "../inc/ldr.h"
#include <stdlib.h>
#include "../inc/timer.h"
#include "../inc/movement.h"
#include "../inc/uart.h"
#include "../inc/remote.h"
extern volatile int button_event, button_num, leftCalVal, rightCalVal;

// Global scan arrays and variables (defined here, declared in header)
float scan_data_ir[91];
float scan_data_ping[91];
struct Object objects[10];
float ir_dist;
float ping_dist;
char has_tape;
bool isTaped[91];


float getLinWidth(int degrees, float dist) {
    return 2*dist*sin(M_PI * degrees/360);
}

void scan_init(void) {
    timer_init();
    servo_init();
    adc_init();
    button_init();
    init_button_interrupts();
    lcd_init();
    ping_init();
}


void scan_cal(void)
{
    int degrees = 90;
    char statFlag = 0, end = 1;

    while (end) {
        if (button_event) {
            if (statFlag == 0) {
                if (button_num == 1) {
                    degrees++;
                }
                else if (button_num == 2) {
                    degrees += 5;
                }
                else if (button_num == 3) {
                    statFlag = 1;
                }
                else if (button_num == 4) {
                    end = 0;
                }
            }
            else {
                if (button_num == 1) {
                                 degrees--;
                }
                else if (button_num == 2) {
                    degrees -= 5;
                }
                else if (button_num == 3) {
                    statFlag = 0;
                }
                else if (button_num == 4) {
                    end = 0;
                }
            }

        }
        lcd_printf("Match Val: %d", servo_move(degrees));
    }
}

void basic_scan(float* irdata, float* pingdata, bool* hasTape) {
    int i = 0;
    for (i = 0; i < 91; i++) {
        servo_move(i*2);
        timer_waitMillis(5);  // Wait for servo to settle before reading different from original
        irdata[i] = convert_IR_Normal(adc_read()); // Adjusted
        pingdata[i] = pingScan();
        hasTape[i] = ir_recv_seen();
        //data[i] = adc_read(); // Raw ADC values for Shuns Boyfriend
    }
}

void quick_scan(float* irdata) {
    int i = 0;
    // Scan from 46° to 134° in 2° increments
    // Array index formula: i = angle / 2
    // So for 46° to 134°, we need indices 23 to 67
    for (i = 23; i < 68; i++) {
        int angle = i * 2;  // Calculate angle (46°, 48°, 50°... 134°)
        servo_move(angle);  // Move servo to angle
        irdata[i] = convert_IR_Normal(adc_read()); // Store IR distance
        
        // Send to GUI immediately for real-time display
        // GUI expects both PING and IR, so we use IR for both (quick scan optimization)
        char scan_msg[80];
        float ir_cm = irdata[i];
        sprintf(scan_msg, "ANGLE=%d: PING=%.2f IR=%.2f TAPE=0\r\n", angle, ir_cm, ir_cm);
        uart_sendStr(scan_msg);
    }
    adrian_clean_function(irdata);
}


void clean_scan_data(float* data) {
    int k;
        for (k = 1; k < 90; k++){
            if (k <= 2) {
                *(data + k -1) = *(data + k+1);
            }
            else if ((fabs(*(data+k) - *(data+k+1)) >.10) && (fabs(*(data + k) - *(data + k - 1) >.10)) && (fabs(*(data + k + 1) - *(data + k - 1) <.10))) {
                *(data + k) = (*(data + k + 1) + *(data + k -1))/2;
            }
        }
}

/**
 * adrian_clean_function - Improved scan data cleaning with better outlier detection
 * 
 * This function removes noise and outliers from IR scan data with improvements over clean_scan_data:
 * 1. Handles all array indices including edges (0 and 90)
 * 2. Better outlier detection using adaptive thresholds
 * 3. Multi-pass cleaning for stubborn outliers
 * 4. Median filtering for extreme spikes
 * 
 * @param data: Array of 91 float values (distances in meters)
 */
void adrian_clean_function(float* data) {
    int i, pass;
    float prev, curr, next;
    
    // PASS 1: Remove extreme outliers (>1.5m difference from neighbors)
    // This catches sensor errors and obvious bad readings
    for (i = 1; i < 90; i++) {
        prev = data[i - 1];
        curr = data[i];
        next = data[i + 1];
        
        // If current reading differs from BOTH neighbors by >1.0m, it's an outlier
        if (fabs(curr - prev) > 1.0 && fabs(curr - next) > 1.0) {
            // Replace with average of neighbors
            data[i] = (prev + next) / 2.0;
        }
    }
    
    // PASS 2: Smooth noise using weighted average
    // This removes smaller spikes and smooths the curve
    for (pass = 0; pass < 2; pass++) {  // 2 passes for better smoothing
        for (i = 1; i < 90; i++) {
            prev = data[i - 1];
            curr = data[i];
            next = data[i + 1];
            
            // If current point differs significantly from neighbors, smooth it
            float diff_prev = fabs(curr - prev);
            float diff_next = fabs(curr - next);
            float diff_neighbors = fabs(prev - next);
            
            // Spike detection: current differs from both neighbors, but neighbors are similar
            if (diff_prev > 0.15 && diff_next > 0.15 && diff_neighbors < 0.20) {
                // Replace spike with average of neighbors
                data[i] = (prev + next) / 2.0;
            }
        }
    }
    
    // PASS 3: Handle edge cases (indices 0 and 90)
    // Use nearest valid neighbor for edge values
    if (fabs(data[0] - data[1]) > 0.5) {
        data[0] = data[1];  // If edge is outlier, copy neighbor
    }
    if (fabs(data[90] - data[89]) > 0.5) {
        data[90] = data[89];  // If edge is outlier, copy neighbor
    }
    
    // PASS 4: Final smoothing with moving average
    // This creates a smoother final curve
    float temp[91];
    for (i = 0; i < 91; i++) {
        temp[i] = data[i];  // Copy to temp array
    }
    
    for (i = 1; i < 90; i++) {
        // Simple 3-point moving average for final smoothing
        data[i] = (temp[i - 1] + temp[i] + temp[i + 1]) / 3.0;
    }
    
    // Keep edges as is after main smoothing
    data[0] = temp[0];
    data[90] = temp[90];
}

void point_scan(int degrees, float* irDist, float* pingVal) {
    servo_move(degrees);
    int irVal = adc_read();
    *irDist = convert_IR_Normal(irVal)/100;
    *pingVal = pingScan();
}

void cal_IR(void) {
    servo_move(90);
    char end = 1;
    int irVal = 0;
    float pingVal = 0;
    while (end){
        irVal = adc_read();
        pingVal = pingScan();
        lcd_printf("IR Val: %d\nPing Dist: %3.2f", irVal, pingVal);

        if (button_num == 4) {
            end = 0;
        }
        timer_waitMillis(100);
    }
}

char is_taped(int irVal, float pingDist) {
    float tapedDist = convert_IR_Taped(irVal);
    float normDist = convert_IR_Normal(irVal);
    float pingToTape = fabsf(pingDist - tapedDist);
    float pingToNorm = fabsf(pingDist - normDist);
    
    return (pingToNorm - pingToTape) > 0;
}
// Anything further than 1 meter is considered no object
void detect_Obj(float* data, struct Object* objects){
    char i = 0, objInt = 0;
    char rEdge, lEdge;
    float redgeDist;
    while (i < 91) {
        if (data[i] < 1.0){
            rEdge = i*2;
            redgeDist = data[i];
            while (fabs(redgeDist - data[i]) < .18){
                i++;
            }
            lEdge = (i-1)*2;
            objects[objInt].angle = (lEdge+rEdge)/2;
            objects[objInt].width = lEdge - rEdge;

            if (objects[objInt].width > 0) {
                point_scan(objects[objInt].angle, &objects[objInt].irVal, &objects[objInt].distance);
                timer_waitMillis(500);
                point_scan(objects[objInt].angle, &objects[objInt].irVal, &objects[objInt].distance);
                objInt++;
            }
        }
        i++;
    }
}
// robot diameter is 3.3 meteres
void second_detect_Obj(float* data, struct Object* objects) {
    int i = 0;
    int objCount = 0;
    int startIndex;
    int k;
    
    // Clear previous object data safety
    for(k=0; k<10; k++) objects[k].width = 0;

    while (i < 91) {
        // Step 1: Find the start of an object (Distance < 1.0m)
        if (data[i] < 1.0) {
            startIndex = i;
            float startDist = data[i];
            
            // Step 2: Find the end of the object
            // We loop AS LONG AS:
            // A. We are still within array bounds (i < 91)
            // B. The distance is still < 1.0m (We haven't hit the void)
            // C. The distance is somewhat close to the start distance (continuity)
            while ( (i < 91) && (data[i] < 1.0) && (fabs(startDist - data[i]) < 0.20) ) {
                i++;
            }
            
            // Step 3: Calculate Object Details
            int endIndex = i - 1;
            int angularWidth = (endIndex - startIndex) * 2; // Assuming 2 degrees per index
            
            // Filter: Only count as an object if it is wider than 2 degrees (noise filter)
            // AND we haven't filled up our object array (max 10)
            if (angularWidth > 2 && objCount < 10) {
                
                // Calculate center angle
                int centerIndex = (startIndex + endIndex) / 2;
                objects[objCount].angle = centerIndex * 2;
                objects[objCount].width = angularWidth; // Angular width
                
                // Store the distance (use the center point distance)
                objects[objCount].distance = data[centerIndex];
                
                // OPTIONAL: Linear Width calculation (Requires your previous function)
                // objects[objCount].linearWidth = getLinWidth(angularWidth, objects[objCount].distance);

                // Perform the confirmation scan
                // Note: Only scan ONCE. No need to sleep and scan twice.
                point_scan(objects[objCount].angle, &objects[objCount].irVal, &objects[objCount].distance);
                
                objCount++;
            }
        } else {
            // If not an object, move to next degree
            i++;
        }
    }
}

// ============================================================================
// GUI-SPECIFIC SCAN COMMANDS (require UART)
// These functions send formatted data over UART for the Python GUI
// ============================================================================

#include "../inc/uart.h"    
#include <stdio.h>
#include "../inc/scan.h"

/**
 * Send scan point data with tape detection info to GUI via UART
 * Format: ANGLE=<deg>: PING=<cm> IR=<cm> TAPE=<0|1>
 * This format is compatible with the Python GUI's parse_and_log_scan_data function
 */
void send_scan_point_with_tape(int angle, float ping_dist, float ir_dist, bool has_tape) {
    char buffer[100];
    sprintf(buffer, "ANGLE=%d: PING=%.2f IR=%.2f TAPE=%d\r\n", angle, ping_dist, ir_dist, has_tape);
    uart_sendStr(buffer);
}

/**
 * Basic scan command (GUI version - collects IR data for radar display)
 * Scans 0-180 degrees, sends IR distance for each angle
 */
void basic_scan_command(void) {
    lcd_printf("Basic Scan\nStarting...");
   
    // Disable hazard reporting during scanning
    disable_hazard_reporting();
    
    // Scan from 0 to 180 with IR sensor
    uart_sendStr("BASIC_SCAN_START\r\n");
    basic_scan(scan_data_ir, scan_data_ping, isTaped);

    // Clean the IR scan data using improved cleaning algorithm
    uart_sendStr("CLEANING_SCAN_DATA\r\n");
    adrian_clean_function(scan_data_ir);
    adrian_clean_function(scan_data_ping);

    // Send all scan points to GUI for radar visualization
    // scan_data[i] is already in meters, so multiply by 100 to get cm
    int i = 0;
    for (i = 0; i < 91; i++) {
        float ir_distance_cm = scan_data_ir[i]; // Convert from meters to cm for display
        //float ir_distance_cm = scan_data[i]; // Testing raw values
        // Send: angle, ping_dist (use IR for display), ir_dist (cleaned data), has_tape
        send_scan_point_with_tape(i * 2, scan_data_ping[i], ir_distance_cm, isTaped[i]);
        timer_waitMillis(5); // Small delay for GUI to process data
    }
    
    uart_sendStr("BASIC_SCAN_COMPLETE\r\n");
    lcd_printf("Basic Scan\nComplete");
    
    // Re-enable hazard reporting after scanning
    enable_hazard_reporting();
}

/**
 * Object detection scan with detailed analysis (GUI command)
 * Workflow: 
 * 1. IR scan all angles for radar background display
 * 2. Clean the data
 * 3. Detect objects and use PING to measure precise distances
 * 4. Send all IR data to GUI for radar background
 * 5. Send detected objects with PING distances and tape detection
 */
void object_detect_command(void) {
    lcd_printf("Object Detect\nScanning...");
    uart_sendStr("OBJECT_DETECT_START\r\n");

    // Disable hazard reporting during scanning
    disable_hazard_reporting();

    // STEP 1: Full IR scan for radar background
    uart_sendStr("STEP_1: IR scan (0-180 deg)...\r\n");
    basic_scan(scan_data_ir, scan_data_ping, isTaped);

    // STEP 2: Clean scan data using improved algorithm
    uart_sendStr("STEP_2: Cleaning data...\r\n");
    // clean_scan_data(scan_data); // Original cleaning (commented out)
    adrian_clean_function(scan_data_ir);

    // STEP 3: Detect objects using PING for precise distance
    uart_sendStr("STEP_3: Detecting objects...\r\n");
    second_detect_Obj(scan_data_ir, objects);
    // adrian_clean_function(scan_data); // Re-clean after object detection

    // STEP 4: Send cleaned IR data for radar display background
    uart_sendStr("STEP_4: Sending radar background (IR only)...\r\n");
    int i = 0;
    for (i = 0; i < 91; i++) {
        // Send IR data as both PING and IR for background display
        float ir_cm = scan_data_ir[i] * 100.0; // Convert to cm
        send_scan_point_with_tape(i * 2, scan_data_ping[i], ir_cm, 0);
        timer_waitMillis(15); // Small delay for GUI processing
    }

    // STEP 5: Send detected objects with PING distance (yellow dots on radar)
    uart_sendStr("STEP_5: Sending detected objects...\r\n");
    int obj_count = 0;
    for (i = 0; i < 10; i++) {
        if (objects[i].width > 0) {
            // Check if object has tape
            char obj_has_tape = is_taped((int)(objects[i].irVal * 100), objects[i].distance);
            
            // Print object details to UART for logging
            char obj_info[120];
            sprintf(obj_info, "OBJ_%d: Angle=%d deg, Width=%d deg, Dist=%.2f cm, IR=%.2f, Tape=%s\r\n", 
                    obj_count + 1, objects[i].angle, objects[i].width, 
                    objects[i].distance, objects[i].irVal, obj_has_tape ? "YES" : "NO");
            uart_sendStr(obj_info);
            
            // Send detected object with PING distance for GUI visualization (yellow marker)
            // The GUI will highlight this as an object based on PING distance
            send_scan_point_with_tape(objects[i].angle, objects[i].distance, objects[i].irVal, obj_has_tape);
            timer_waitMillis(100);
            
            obj_count++;
        }
    }
    
    // Summary 
    char summary[50];
    sprintf(summary, "OBJECTS_FOUND: %d\r\n", obj_count);
    uart_sendStr(summary);
    
    uart_sendStr("OBJECT_DETECT_COMPLETE\r\n");
    lcd_printf("Found %d obj\nScan complete", obj_count);
    
    // Re-enable hazard reporting after scanning
    enable_hazard_reporting();
}

/**
 * Tape detection command (GUI version) - Updated for single angle checking
 * Performs a point scan at the specified angle and checks for tape
 * PRESERVES existing radar display by not sending full scan data
 */
// void tape_detect_command(int angle) {
//     uart_sendStr("TAPE_DETECT_START\r\n");
//     lcd_printf("Tape Check\nAngle: %d deg", angle);

//     // Disable hazard reporting during tape detection
//     disable_hazard_reporting();

//     // Validate angle range
//     if (angle < 0 || angle > 180) {
//         uart_sendStr("ERROR: Invalid angle. Must be 0-180 degrees.\r\n");
//         lcd_printf("Invalid angle\nRange: 0-180 deg");
//         enable_hazard_reporting(); // Re-enable before returning
//         return;
//     }

//     char status_msg[60];
//     sprintf(status_msg, "Checking for tape at %d degrees...\r\n", angle);
//     uart_sendStr(status_msg);

//     // Move servo to the specified angle
//     servo_move(angle);
//     timer_waitMillis(750); // Wait for servo to reach position and stabilize

//     // Take IR and PING readings at this angle
//     int irVal = adc_read();
//     float ping_dist = pingScan();
//     int irSUM = 0;
//     int i = 0;
//     for (i = 0; i < 5; i++) {
//         irSUM += adc_read();
//         timer_waitMillis(300); // Brief pause between readings
//     }
//     irVal = irSUM / 5;

//     // Take a second reading for accuracy
//     float ping_dist2 = pingScan();
    
//     // Average the readings for better accuracy
//     float avg_ping_dist = (ping_dist + ping_dist2) / 2.0;
    
//     // Check if there's tape at this angle using averaged readings
//     char has_tape = is_taped(irVal, avg_ping_dist);
    
//     // Convert distances to cm for display
//     float ping_cm = avg_ping_dist;
    
//     // Send detailed tape detection result
//     char tape_result[150];
//     sprintf(tape_result, "TAPE_RESULT:  Tape=%s\r\n", has_tape ? "DETECTED" : "NOT_FOUND");
//     uart_sendStr(tape_result);
    
//     uart_sendStr("TAPE_DETECT_COMPLETE\r\n");
//     lcd_printf("Tape: %s\n%.1f cm", has_tape ? "FOUND" : "NONE", ping_cm);
    
//     // Re-enable hazard reporting after tape detection
//     enable_hazard_reporting();
// }

void tape_detect_command(int angle)
{
    uart_sendStr("TAPE_DETECT_START\r\n");
    lcd_printf("Tape Check\nAngle: %d deg", angle);

    // Disable hazard reporting during tape detection
    disable_hazard_reporting();

    // Validate angle range
    if (angle < 0 || angle > 180) {
        uart_sendStr("ERROR: Invalid angle. Must be 0-180 degrees.\r\n");
        lcd_printf("Invalid angle\nRange: 0-180 deg");
        enable_hazard_reporting();
        return;
    }

    char status_msg[60];
    sprintf(status_msg, "Checking for tape at %d degrees...\r\n", angle);
    uart_sendStr(status_msg);

    // Move servo to the specified angle
    servo_move(angle);
    timer_waitMillis(750); // Wait for servo to reach position and stabilize

    // Take IR and LDR readings at this angle
    uint16_t ir_raw = adc_read();
    uint16_t ldr_raw = ldr_read_raw();
    uint8_t cls = ldr_detect_surface();

    // Take multiple readings for better accuracy
    int irSum = 0;
    int i = 0;
    for (i = 0; i < 5; i++) {
        irSum += adc_read();
        timer_waitMillis(300);
    }
    int irVal = irSum / 5;

    // Take PING readings for distance verification
    float ping_dist = pingScan();
    timer_waitMillis(100);
    float ping_dist2 = pingScan();
    float avg_ping_dist = (ping_dist + ping_dist2) / 2.0;

    // Determine if tape is present using LDR classification
    char has_tape = 0;
    char tape_status[20];

    if (cls == 1) {  // LDR_DARK_TAPE
        // Almost certainly on black electrical tape PVC
        has_tape = 1;
        sprintf(tape_status, "DARK_TAPE");
    }
    else if (cls == 2) {  // LDR_PLAIN_PVC
        // Plain PVC (no tape)
        has_tape = 0;
        sprintf(tape_status, "PLAIN_PVC");
    }
    else {
        // UNKNOWN: fall back to old IR-only logic
        has_tape = is_taped(irVal, avg_ping_dist);
        sprintf(tape_status, "UNKNOWN_IR");
    }

    // Convert distances to cm for display
    float ping_cm = avg_ping_dist;

    // Send detailed tape detection result
    char tape_result[150];
    sprintf(tape_result, "TAPE_RESULT: Tape=%s Status=%s IR=%u LDR=%u Ping=%.2f\r\n",
            has_tape ? "DETECTED" : "NOT_FOUND", tape_status, ir_raw, ldr_raw, ping_cm);
    uart_sendStr(tape_result);

    uart_sendStr("TAPE_DETECT_COMPLETE\r\n");
    lcd_printf("Tape: %s\n%.1f cm", has_tape ? "FOUND" : "NONE", ping_cm);

    // Re-enable hazard reporting after tape detection
    enable_hazard_reporting();
}
