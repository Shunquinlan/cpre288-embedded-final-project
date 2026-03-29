/*
 * adc.c
 *
 *  Created on: Oct 21, 2025
 *      Author: ngratz01
 */

#include "../inc/adc.h"

void adc_init(void) {
    SYSCTL_RCGCGPIO_R |= 0b000010;
    SYSCTL_RCGCADC_R |= 0b01;

    GPIO_PORTB_AFSEL_R |= 0b0001000;
    GPIO_PORTB_DEN_R &= 0b1110111;
    GPIO_PORTB_AMSEL_R |= 0b0001000;
    GPIO_PORTB_ADCCTL_R &= 0x00;

    ADC0_ACTSS_R = 0b0010;
    ADC0_EMUX_R  = 0x0000;
    ADC0_SSMUX1_R = 0xAAAA;
    ADC0_SSCTL1_R = 0x6000;

    ADC0_IM_R |= 0b0010;
    ADC0_ISC_R |= 0b0010;

    ADC0_SAC_R |= 0x6; //avg 64 samples
}

int adc_read(void) {
    ADC0_PSSI_R |= 0b0010;
    while ((ADC0_SSFSTAT1_R & 0x1000) == 0);
    return ADC0_SSFIFO1_R;
}

float convert_IR_Normal(int iVal) {
    // return 2408.3 * pow(iVal, -0.718);  // Box
    return 2981.8 * pow(iVal, -0.751);  // Cylinder

}

float convert_IR_Taped(int iVal) {
    // return 1237.2 * pow(iVal, -0.655); // Box
    return 2460.7 * pow(iVal, -0.741); // Cylinder

}
