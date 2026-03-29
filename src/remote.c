// dual_ir_live.c
// Show analog IR raw value and "remote present" flag in PuTTY.
// Columns: analog_raw   recv_on (0/1)

#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include "inc/tm4c123gh6pm.h"
#include "../inc/timer.h"
#include "../inc/uart.h"
#include "../inc/scan.h"

// ------------ UART helper -------------
static void sendString(const char *s) {
    while (*s) uart_sendChar(*s++);
}


void ir_recv_init(void)
{
    // Enable Port c clock
    SYSCTL_RCGCGPIO_R |= 0b100;
    

    // PC7 as digital input
    GPIO_PORTC_DIR_R &= ~0b01000000;   // input
    GPIO_PORTC_DEN_R |=  0b01000000;   // digital enable
    
}

// active-LOW: returns true when IR is present
bool ir_recv_seen(void)
{
    return (GPIO_PORTC_DATA_R & 0b01000000) ? false : true;
}

// int main(void)
// {
//     timer_init();
//     uart_init();
//     ir_recv_init();

//     // Init CyBot scan (Ping + analog IR). Use your mask.
//     cyBOT_init_Scan(0b0111);

//     // *** set your bot's servo calibration values ***
//     extern int right_calibration_value;
//     extern int left_calibration_value;
//     right_calibration_value = 248500;   // Bot 8 example
//     left_calibration_value  = 1198750;  // change to your bot if needed

//     sendString("\r\n=== Dual IR LIVE Test ===\r\n");
//     sendString("Columns:  analog_raw   recv_on(0/1)\r\n\r\n");

//     cyBOT_Scan_t scan;

//     while (1) {

//         // 1) Get analog IR reading at 90�
//         cyBOT_Scan(90, &scan);
//         timer_waitMillis(5);                // tiny settle
//         int analog_raw = scan.IR_raw_val;   // old IR sensor raw value

//         // 2) Watch receiver for ~100 ms
//         bool any_seen = false;
//         int i;
//         for (i = 0; i < 100; i++) {     // 100 * 1 ms = 100 ms
//             if (ir_recv_seen()) any_seen = true;
//             timer_waitMillis(1);
//         }

//         int recv_on = any_seen ? 1 : 0;

//         // 3) Print in two columns
//         char line[64];
//         sprintf(line, "%6d        %d\r\n", analog_raw, recv_on);
//         sendString(line);
//         // Loop repeats: you get a new line about every 100 ms
//     }
// }
