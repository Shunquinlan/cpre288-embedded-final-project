/*
 * servo.c
 *
 *  Created on: Nov 4, 2025
 *      Author: ngratz01
 */

#include "../inc/servo.h"
//Cybot 14
//Match at 0 = 311568
//Match at 180 = 282792
volatile int rightCalVal = 311568;
volatile int leftCalVal = 282792;
//testing

void servo_init(void) {
    timer_init();
    SYSCTL_RCGCGPIO_R |= 0b000010;
    SYSCTL_RCGCTIMER_R |= 0x02;

    GPIO_PORTB_DEN_R |= 0b00100000;
    GPIO_PORTB_DIR_R |= 0b00100000;

    GPIO_PORTB_AFSEL_R |= 0b00100000;
    GPIO_PORTB_PCTL_R &= 0xFF7FFFFF;
    GPIO_PORTB_PCTL_R |= 0x00700000;

    TIMER1_CTL_R &= ~0x100;
    TIMER1_CFG_R = 0x4;

    TIMER1_TBMR_R = 0xA;

    TIMER1_CTL_R &= ~0x4000;
    TIMER1_TBPR_R = 0x04;
    TIMER1_TBILR_R = 0xE200;

}

int servo_move(int degrees) {
    int pW, lowWidth;
    int leftVal = 320000 - leftCalVal;
    int rightVal = 320000 - rightCalVal;

    TIMER1_CTL_R &= ~0x100;

    pW = (((leftVal - rightVal)/180) * degrees + (320000 - rightCalVal));
    lowWidth = 320000 - pW;

    TIMER1_TBPMR_R = (lowWidth >> 16);
    TIMER1_TBMATCHR_R = lowWidth - ((lowWidth >> 16) << 16);
    TIMER1_CTL_R |= 0x100;

    timer_waitMillis(50);

    return lowWidth;

}

