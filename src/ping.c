/*
 * ping.c
 *
 *  Created on: Oct 28, 2025
 *      Author: ngratz01
 */
#include "../inc/timer.h"
#include "../inc/ping.h"

volatile enum  Status {FIRST, SECOND, END} state;
volatile int startPulse, endPulse, overCount;

void ping_init(void) {

    timer_init();
    SYSCTL_RCGCGPIO_R |= 0x02;
    SYSCTL_RCGCTIMER_R |= 0x08;


    overCount = 0;

    GPIO_PORTB_AFSEL_R &= ~0x08;
    GPIO_PORTB_PCTL_R &= ~0x0000F000;
    GPIO_PORTB_DIR_R |= 0x08;
    GPIO_PORTB_DEN_R |= 0x08;
    GPIO_PORTB_DATA_R &= ~0x08;


    TIMER3_CTL_R &= ~0x100;
    TIMER3_CFG_R = 0x00000004;


    TIMER3_TBMR_R = 0x07;

    TIMER3_CTL_R |= 0xC00;
    TIMER3_TBILR_R = 0xFFFF;
    TIMER3_TBPR_R = 0xFF;

    TIMER3_IMR_R = 0x500;
    TIMER3_ICR_R = 0x500;
    TIMER3_CTL_R |= 0x100;
    NVIC_EN1_R |= 0x10;

    IntRegister(INT_TIMER3B, timer3BHandler);

}

void pingSend(void) {

    TIMER3_IMR_R &= 0xBFF;
    GPIO_PORTB_AFSEL_R &= ~0x08;
        GPIO_PORTB_DIR_R |= 0x08;


        GPIO_PORTB_DATA_R |= 0x08;
        timer_waitMillis(1);
        GPIO_PORTB_DATA_R &= ~0x08;


        GPIO_PORTB_AFSEL_R |= 0x08;
        GPIO_PORTB_DIR_R &= ~0x08;
        GPIO_PORTB_PCTL_R &= ~0x0000F000;
        GPIO_PORTB_PCTL_R |= 0x00007000;


        TIMER3_ICR_R = 0x500;
        TIMER3_IMR_R = 0x500;

}

float pingScan(void)
{

    int pW = 0;
    state = FIRST;

    pingSend();

    while (state != END);
    timer_waitMillis(50);
    pW =startPulse - endPulse;
    if ( pW < 0){
        pW += 0xFFFFFF;
        overCount++;
    }
    state = FIRST;
	return pW * 17/16000.0;
}

void timer3BHandler(void) {


    if (TIMER3_MIS_R & 0x400) {

        TIMER3_ICR_R = 0x400;

        if (state == FIRST) {
            startPulse = TIMER3_TBR_R;

            state = SECOND;

        } else if (state == SECOND) {
            endPulse = TIMER3_TBR_R;
            state = END;
            TIMER3_IMR_R &= ~0x400;

            GPIO_PORTB_AFSEL_R &= ~0x08;
            GPIO_PORTB_DIR_R |= 0x08;
        }
    }
    if (TIMER3_MIS_R & 0x100){
            overCount++;
            TIMER3_ICR_R = 0x100;
        }
}

