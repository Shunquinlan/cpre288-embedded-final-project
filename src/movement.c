// movement.c (clean, single-speed, original structure)
#include "../inc/open_interface.h"
#include "../inc/movement.h"
#include "../inc/timer.h"
#include "../inc/cliff.h"
#include "../inc/led.h"
#include "../inc/sound.h"
#include "../inc/uart.h"
#include "../inc/scan.h"
#include <math.h>
#include <stdio.h>  // for sprintf

// ====== Tunables ======
#define FWD_SPEED           100      // straight-line wheel speed
#define TURN_SPEED           90      // spin-in-place wheel speed
#define ANGLE_TOL_DEG       1.0      // stop when within this many degrees
#define STOP_SETTLE_MS     150       // pause after a stop to kill inertia

// NOTE: Most labs report sensor->distance in millimeters.
// Using 10 mm per cm keeps math unambiguous.
#define MM_PER_CM           10

// ========= Tunables =========
#define STEP_CM   5
#define STEP_DEG  5

// On your bot: when it is over the black/border line,
// FL/FR were > 2300. Adjust this number if needed.
#define BORDER_THRESH 2600

// ================= FUNCTION DECLARATIONS =====================

static bool is_on_white_border(const oi_t *sensor);
static void avoid_bump_obstacle(oi_t *sensor);
static void avoid_cliff_obstacle(oi_t *sensor);
static void move_forward_exit_final(oi_t *sensor, int cm);

// ================= HAZARD REPORTING CONTROL =====================

static bool hazard_reporting_enabled = true;

void enable_hazard_reporting(void) {
    hazard_reporting_enabled = true;
}

void disable_hazard_reporting(void) {
    hazard_reporting_enabled = false;
}

bool is_hazard_reporting_enabled(void) {
    return hazard_reporting_enabled;
}

// ================= GUI HAZARD REPORT =====================

static void gui_report_hazard(oi_t *sensor)
{
    // Don't report hazards during scanning operations
    if (!hazard_reporting_enabled) {
        return;
    }
    
    const char *type = "NONE";
    const char *side = "NA";

    // -------- 1) BUMP --------
    if (sensor->bumpLeft || sensor->bumpRight) {
        type = "BUMP";

        if (sensor->bumpLeft && sensor->bumpRight) {
            side = "BOTH";
        } else if (sensor->bumpLeft) {
            side = "LEFT";
        } else if (sensor->bumpRight) {
            side = "RIGHT";
        }
    }
    // -------- 2) CLIFF / BLACK TAPE (holes) --------
    else if (sensor->cliffLeft || 
             sensor->cliffFrontLeft || 
             sensor->cliffFrontRight || 
             sensor->cliffRight) {

        type = "HOLE";  // Digital cliff sensors detect holes/black tape

        int L  = sensor->cliffLeft;
        int FL = sensor->cliffFrontLeft;
        int FR = sensor->cliffFrontRight;
        int R  = sensor->cliffRight;

        if ((FL || L) && !(FR || R)) {
            side = "LEFT";
        } else if ((FR || R) && !(FL || L)) {
            side = "RIGHT";
        } else {
            side = "CENTER";   // ahead or multiple sensors
        }
    }
    // -------- 3) WHITE BORDER (analog cliff signals - edges) --------
    else if (is_on_white_border(sensor)) {
        type = "EDGE";  // Analog cliff signals detect white tape edges

        int left_on  = (sensor->cliffLeftSignal      > BORDER_THRESH) ||
                       (sensor->cliffFrontLeftSignal > BORDER_THRESH);
        int right_on = (sensor->cliffRightSignal     > BORDER_THRESH) ||
                       (sensor->cliffFrontRightSignal> BORDER_THRESH);

        if (left_on && right_on) {
            side = "BOTH";
        } else if (left_on) {
            side = "LEFT";
        } else if (right_on) {
            side = "RIGHT";
        }
    }

    // -------- Send to GUI over UART --------
    char msg[64];
    sprintf(msg, "HZ,%s,%s\r\n", type, side);
    uart_sendStr(msg);   // Send hazard report to GUI
}

// --- small helper ---
static inline void stop_and_settle(int ms) {
    oi_setWheels(0, 0);
    timer_waitMillis(ms);
}

// ------------------------
// High-level bump reaction
// ------------------------

void move_forward(oi_t *sensor, int cm)
{
    double s = 0;
    oi_setWheels(FWD_SPEED, FWD_SPEED);
    while (s < (cm * MM_PER_CM)) {
        oi_update(sensor);

        s += sensor->distance;
    }
    stop_and_settle(10);
}

void move_backward(oi_t *sensor, int cm)
{
    double s = 0;
    oi_setWheels(-FWD_SPEED, -FWD_SPEED);
    while (s > -(cm * MM_PER_CM)) {
        oi_update(sensor);
        s += sensor->distance;
    }
    stop_and_settle(50);
}

// -------------------
// Single-speed turns
// -------------------
double turn_right(oi_t *sensor, double deg)  // returns actual positive degrees
{
    if (deg < 0) deg = -deg;

    oi_update(sensor);              // zero incremental angle
    double a = 0.0;

    oi_setWheels(-TURN_SPEED, TURN_SPEED);  // spin CW
    while (a < (deg - ANGLE_TOL_DEG)) {
        oi_update(sensor);
        a += -sensor->angle;        // right-turn is negative from the robot
        if (a < 0) a = 0;           // clamp noise on first sample
    }
    stop_and_settle(STOP_SETTLE_MS);
    return a;
}

double turn_left(oi_t *sensor, double deg)   // returns actual positive degrees
{
    if (deg < 0) deg = -deg;

    oi_update(sensor);
    double a = 0.0;

    oi_setWheels(TURN_SPEED, -TURN_SPEED);   // spin CCW
    while (a < (deg - ANGLE_TOL_DEG)) {
        oi_update(sensor);
        a += sensor->angle;         // left-turn is positive
        if (a < 0) a = 0;
    }
    stop_and_settle(STOP_SETTLE_MS);
    return a;
}

// ------------------------
// Enhanced movement with cliff detection
// ------------------------


void safe_move_backward(oi_t *sensor, int cm)
{
    double s = 0;
    oi_setWheels(-FWD_SPEED, -FWD_SPEED);
    while (s > -(cm * MM_PER_CM)) {
        oi_update(sensor);
        
        // Check for rear bumps or cliffs when moving backward
        if (sensor->bumpLeft || sensor->bumpRight) {
            // Hit something while backing up
            led_red();
            sound_play_error();
            uart_sendStr("BUMP DETECTED (REAR)!\r\n");
            oi_setWheels(0, 0);
            return;
        }
        
        s += sensor->distance;
    }
    stop_and_settle(50);
    led_off();
}

void explore_with_cliff_avoidance(oi_t *sensor)
{
    int i;
    // Simple exploration algorithm with cliff avoidance
    for (i = 0; i < 4; i++) {
        // Try to move forward
        move_forward_safe(sensor, 20); // Try 20 cm
        
        // Check if we hit a cliff and stopped early
        oi_update(sensor);
        if (cliff_found(sensor)) {
            // Back away from cliff
            safe_move_backward(sensor, 5);
            
            // Turn to avoid the cliff
            turn_right(sensor, 90);
        }
        
        // Small delay between movements
        timer_waitMillis(500);
    }
}

// ========= Forward with safety =========
//
// Drives forward up to "cm" but stops early if:
//   - bump hit   -> returns 1
//   - border hit -> returns 2  
//   - no issue   -> returns 0
//
// Also updates global variables for detailed reporting:
// - actual_distance_traveled_mm: actual distance traveled in mm
// - bump_side: 1=left, 2=right, 3=both, 0=none (set by gui_report_hazard)
//
int actual_distance_traveled_mm = 0;
int bump_side = 0;

int move_forward_safe(oi_t *sensor, int cm)
{
    double sum_mm = 0.0;
    int reason = 0;  // 0=OK, 1=bump, 2=border
    
    // Reset globals
    actual_distance_traveled_mm = 0;
    bump_side = 0;

    // Start moving: yellow LED, but NO OK sound yet
    led_yellow();
    oi_setWheels(100, 100);

    while (sum_mm < cm * 10) { // cm -> mm
        oi_update(sensor);
        sum_mm += sensor->distance;

        // 1) bump check with side detection
        if (sensor->bumpLeft || sensor->bumpRight) {
            reason = 1;
            
            // Set bump_side: 1=left, 2=right, 3=both
            if (sensor->bumpLeft && sensor->bumpRight) {
                bump_side = 3;  // both bumpers
            } else if (sensor->bumpLeft) {
                bump_side = 1;  // left only
            } else if (sensor->bumpRight) {
                bump_side = 2;  // right only
            }
            break;
        }

        // 2) border check using any cliff SIGNAL > threshold (WHITE tape)
        if (is_on_white_border(sensor)) {
            reason = 2;
            break;
        }

        // 3) Cliff hole detection using digital cliff sensors
        if (sensor->cliffLeft || sensor->cliffFrontLeft || 
            sensor->cliffFrontRight || sensor->cliffRight) {
            reason = 3;
            break;
        }
    }

    // Stop wheels
    oi_setWheels(0, 0);
    
    // Record actual distance traveled
    actual_distance_traveled_mm = (int)sum_mm;

    if (reason != 0) {
        // Trouble: red LED + error sound
        led_red();
        sound_play_error();

        // Report hazard to GUI with detailed side information
        gui_report_hazard(sensor);

        // Back up ~3 cm to get off the line / obstacle
        oi_setWheels(-100, -100);
        timer_waitMillis(300);
        oi_setWheels(0, 0);
    } else {
        // No problem: lights off + OK beep to confirm success
        led_off();
        sound_play_ok();
    }

    return reason;
}


static bool is_on_white_border(const oi_t *sensor)
{
    return (sensor->cliffLeftSignal       > BORDER_THRESH ||
            sensor->cliffFrontLeftSignal  > BORDER_THRESH ||
            sensor->cliffFrontRightSignal > BORDER_THRESH ||
            sensor->cliffRightSignal      > BORDER_THRESH);
}

#define OBST_BACKUP_CM       10
#define OBST_TURN_SMALL_DEG  30
#define OBST_TURN_LARGE_DEG  60

static void avoid_bump_obstacle(oi_t *sensor)
{
    int left  = sensor->bumpLeft;
    int right = sensor->bumpRight;

    led_red();
    sound_play_error();

    // Report bump hazard to GUI
    gui_report_hazard(sensor);

    // Back away from the obstacle
    move_backward(sensor, OBST_BACKUP_CM);

    if (left && !right) {
        // Obstacle on left -> turn right a bit
        turn_right(sensor, OBST_TURN_SMALL_DEG);
    } else if (right && !left) {
        // Obstacle on right -> turn left a bit
        turn_left(sensor, OBST_TURN_SMALL_DEG);
    } else {
        // Both bumps or unknown -> bigger turn to one side
        turn_left(sensor, OBST_TURN_LARGE_DEG);
    }
}

static void avoid_cliff_obstacle(oi_t *sensor)
{
    int L  = sensor->cliffLeft;
    int FL = sensor->cliffFrontLeft;
    int FR = sensor->cliffFrontRight;
    int R  = sensor->cliffRight;

    led_red();
    sound_play_error();

    // Report cliff hazard to GUI
    gui_report_hazard(sensor);

    // Back away from the hole / black tape
    move_backward(sensor, OBST_BACKUP_CM);

    // Decide which way to steer based on where the hole is.
    if ((FL || L) && !(FR || R)) {
        // Hole mostly on LEFT side -> steer RIGHT
        turn_right(sensor, OBST_TURN_SMALL_DEG);
    } else if ((FR || R) && !(FL || L)) {
        // Hole mostly on RIGHT side -> steer LEFT
        turn_left(sensor, OBST_TURN_SMALL_DEG);
    } else {
        // Hole straight ahead or both sides -> bigger turn
        turn_left(sensor, OBST_TURN_LARGE_DEG);
    }
}

#define EXTRA_AFTER_EXIT_CM  35

// ---- Manual EXIT white-border tracking (ASSIGN HERE) ----
static int  manual_white_cross_count = 0;
static bool manual_prev_white        = false;

// ========= Forward ignoring white border (manual 'ASSIGN HERE') =========
//
// Drives forward up to "cm" while:
//   - still stopping for bump or cliff / hole
//   - completely ignoring the white-tape border (all 4 signals)
// SOUND:
//   - plays EXIT sound at start (short cue, then waits ~1s)
//   - if bump or cliff happens, immediately stops, calls avoid_*,
//     and returns (no extra shove)
// EXTRA BEHAVIOR:
//   - tracks how many white borders have been crossed in manual exit
//   - after we LEAVE the SECOND white border:
//        -> stop
//        -> auto-drive EXTRA_AFTER_EXIT_CM forward (still bump/cliff safe)
//        -> stop, show "Soldier down", play soldier-down theme
//        -> reset manual_white_cross_count so you can do it again later
//
static void move_forward_exit_final(oi_t *sensor, int cm)
{
    double sum_mm = 0.0;
    int reason = 0;

    // Keep green LED, no extra exit chime here
    oi_setWheels(100, 100);

    while (sum_mm < cm * 10) {
        oi_update(sensor);
        sum_mm += sensor->distance;

        if (sensor->bumpLeft || sensor->bumpRight) {
            reason = 1;
            avoid_bump_obstacle(sensor);
            break;
        }

        if (sensor->cliffLeft ||
            sensor->cliffRight ||
            sensor->cliffFrontLeft ||
            sensor->cliffFrontRight) {
            reason = 2;
            avoid_cliff_obstacle(sensor);
            break;
        }
    }

    oi_setWheels(0, 0);
    
    // Mission complete - log and play theme
    uart_sendStr("EXIT: Mission Complete!\r\n");
    sound_play_end_mission(); // Mission complete sound

    // avoid_* already handled error sound + recovery
    (void)reason; // silence unused warning; we don't need it here
}

static int  manual_border_state   = 0;   // 0..3 like auto
static bool manual_was_white      = false;
static bool manual_final_done     = false;

int move_forward_exit(oi_t *sensor, int cm)
{
    double sum_mm = 0.0;
    int reason = 0;  // 0 = OK, 1 = bump, 2 = cliff/hole

    // Signal that we are in EXIT mode
    led_green();          // green ONLY while exiting
    sound_play_exit();    // short, distinct exit cue

    // Start moving forward
    oi_setWheels(100, 100);

    while (sum_mm < cm * 10) {   // cm -> mm
        oi_update(sensor);
        sum_mm += sensor->distance;

        // 1) bump check (still active)  SAME logic as auto (avoid_*).
        if (sensor->bumpLeft || sensor->bumpRight) {
            reason = 1;
            avoid_bump_obstacle(sensor);   // same error sound as auto
            break;
        }

        // 2) cliff / hole check using the digital cliff flags (BLACK)
        if (sensor->cliffLeft ||
            sensor->cliffRight ||
            sensor->cliffFrontLeft ||
            sensor->cliffFrontRight) {

            reason = 2;
            avoid_cliff_obstacle(sensor);  // same error sound as auto
            break;
        }

        // 3) Manual white-border tracking over multiple 'e' presses
        if (!manual_final_done) {
            bool is_white = is_on_white_border(sensor);

            switch (manual_border_state) {
            case 0: // looking for first tape
                if (is_white && !manual_was_white) {
                    manual_border_state = 1;  // entered first white tape
                }
                break;

            case 1: // on first tape, wait until we leave it
                if (!is_white && manual_was_white) {
                    manual_border_state = 2;  // between tapes
                }
                break;

            case 2: // between first and second tapes
                if (is_white && !manual_was_white) {
                    manual_border_state = 3;  // on second tape
                }
                break;

            case 3: // on second tape
                if (!is_white && manual_was_white) {
                    // Just left SECOND white tape in manual exit mode.
                    // -> Run the final 35cm + soldier-down, then we're DONE.

                    oi_setWheels(0, 0);
                    manual_final_done = true;

                    led_green();
                    move_forward_exit_final(sensor, EXTRA_AFTER_EXIT_CM);

                    oi_setWheels(0, 0);
                    led_green();
                    uart_sendStr("EXIT: Mission Complete! (Manual Exit)\r\n");
                    sound_play_soldier_down();
                    return 0;   // treat as successful mission
                }
                break;
            }

            manual_was_white = is_white;
        }
    }

    // Stop wheels if we just finished the cm target or hit hazard
    oi_setWheels(0, 0);

    if (reason != 0) {
        // avoid_* already did LED + error sound + recovery.
        return reason;
    } else {
        // Finished step with no obstacle and no double-border completion.
        // Stay green to show we're still in EXIT mode.
        led_green();
        return 0;
    }
}

// ========= Fully automatic EXIT FIELD =========
//
// Auto mode:
//   - drives forward ignoring WHITE border as an obstacle
//   - counts crossing TWO white borders using all 4 analog signals
//   - avoids obstacles with avoid_*
//   - listens for 'z' from GUI: halt auto and return to manual control
//   - performs quick scans (45-135°) periodically while moving
//   - sends scan data to GUI for real-time radar display
//   - after leaving second border (and no 'z'):
//        -> moves EXTRA_AFTER_EXIT_CM
//        -> stops, "Soldier down", soldier-down theme
//
// Returns:
//   0   : success (double border + 35cm + soldier)
//  -1   : failure (distance limit)
//  -2   : halted by user with 'z'
//
int auto_exit_field(oi_t *sensor)
{
    double sum_mm = 0.0;

    led_green();          // exiting mode: green only
    sound_play_exit();    // short cue that auto exit started

    // State machine for white tape:
    //   0 = inside, no tape yet
    //   1 = on first tape
    //   2 = between first and second tape
    //   3 = on second tape
    int state = 0;
    bool was_white = false;

    // Scan tracking variables
    double last_scan_dist_mm = 0.0;
    const double SCAN_INTERVAL_MM = 100.0;  // Scan every 10 cm
    
    // Access global scan array (defined in scan.c)
    extern float scan_data_ir[91];
    
    // Disable hazard reporting during scanning to avoid false positives
    disable_hazard_reporting();

    oi_setWheels(100, 100);   // drive straight out

    while (1) {
        oi_update(sensor);
        sum_mm += sensor->distance;

        // ---- CHECK FOR HALT COMMAND ----
        char incoming = uart_receive();
        if (incoming == 'z' || incoming == 'h') {
            // User requested halt
            oi_setWheels(0, 0);
            led_off();
            servo_move(90);  // Return servo to center
            enable_hazard_reporting();  // Re-enable hazard reporting
            uart_sendStr("HALT: Auto exit stopped by user\r\n");
            return -2;  // halted by user
        }

        // ---- PERIODIC QUICK SCAN (46-134 degrees) ----
        if (sum_mm - last_scan_dist_mm >= SCAN_INTERVAL_MM) {
            // Time for another scan
            uart_sendStr("EXIT_SCAN_START\r\n");
            
            // Call quick_scan which will scan 46° to 134° and send data to GUI
            quick_scan(scan_data_ir);
            
            uart_sendStr("EXIT_SCAN_COMPLETE\r\n");
            
            // Return servo to center position
            servo_move(90);
            
            last_scan_dist_mm = sum_mm;
        }

        // ---- Safety + obstacle avoidance ----

        // 1) BUMP obstacle
        if (sensor->bumpLeft || sensor->bumpRight) {
            avoid_bump_obstacle(sensor);

            // After avoidance, resume AUTO EXIT state
            led_green();
            sound_play_exit();
            oi_setWheels(100, 100);

            // Reset distance segment + white memory
            sum_mm    = 0.0;
            was_white = false;
            continue;
        }

        // 2) CLIFF / BLACK TAPE obstacle
        if (sensor->cliffLeft || sensor->cliffRight ||
            sensor->cliffFrontLeft || sensor->cliffFrontRight) {

            avoid_cliff_obstacle(sensor);

            led_green();
            sound_play_exit();
            oi_setWheels(100, 100);

            sum_mm    = 0.0;
            was_white = false;
            continue;
        }

        // ---- White border detection for field exit (all 4 sensors) ----
        bool is_white = is_on_white_border(sensor);

        switch (state) {
        case 0:  // looking for first tape
            if (is_white && !was_white) {
                state = 1;    // entered first white tape
            }
            break;

        case 1:  // on first tape, wait until we leave it
            if (!is_white && was_white) {
                state = 2;    // now between tapes
            }
            break;

        case 2:  // between first and second tapes
            if (is_white && !was_white) {
                state = 3;    // entered second tape
            }
            break;

        case 3:  // on second tape
            if (!is_white && was_white) {
                // Just left second tape -> all 4 sensors off white

                // 1) Stop briefly
                oi_setWheels(0, 0);
                servo_move(90);  // Return servo to center
                enable_hazard_reporting();  // Re-enable hazard reporting

                // 2) Move extra forward 35 cm, still checking bump / cliff / black tape
                led_green();
                move_forward_exit_final(sensor, EXTRA_AFTER_EXIT_CM);

                // 3) Final stop + soldier-down theme
                oi_setWheels(0, 0);
                led_green();
                uart_sendStr("EXIT: Mission Complete! (Auto Exit Field)\r\n");
                sound_play_end_mission();
                return 0;     // successful auto exit
            }
            break;
        }
        was_white = is_white;
    }
}

