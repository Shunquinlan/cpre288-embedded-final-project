/*
*
*   uart.c
*
*
*
*
*
*   @author
*   @date
*/

#include "../inc/uart.h"

volatile char uartEvent = 0;
void uart_init(void){
	SYSCTL_RCGCGPIO_R |= 0b000010;
	SYSCTL_RCGCUART_R |= 0b000010;

	GPIO_PORTB_AFSEL_R |= 0b00000011;
	GPIO_PORTB_PCTL_R &= 0xFFFFFFEE;
	GPIO_PORTB_PCTL_R |= 0x00000011;
	GPIO_PORTB_DEN_R |= 0b00000011;
	GPIO_PORTB_DIR_R &= 0b11111110;
	GPIO_PORTB_DIR_R |= 0b00000010;

	UART1_IM_R |= 0b0000000010000;
	UART1_IM_R &= 0xFFFFE8DD;
	UART1_ICR_R |= 0b010000;
	NVIC_EN0_R |= 0b01000000;



    double fbrd;
    int    ibrd;

    fbrd = 0.6805556; // page 903
    ibrd = 8;

    UART1_CTL_R &= 0xFFFFFFFE;      // disable UART1 (page 918)
    UART1_IBRD_R |= 0x0008;        // write integer portion of BRD to IBRD
    UART1_IBRD_R &= 0xFFFF0008;
    UART1_FBRD_R |= 0b101100;
    UART1_FBRD_R &= 0xFFFFFFEC;   // write fractional portion of BRD to FBRD
    UART1_LCRH_R &= 0xFFFFFFFC;        // write serial communication parameters (page 916) * 8bit and no parity
    UART1_LCRH_R |= 0x00000060;
    UART1_CC_R   &= 0xFFFFFFF0;          // use system clock as clock source (page 939)
    UART1_CTL_R |= 0b01;        // enable UART1

    IntRegister(INT_UART1, uart_Handler);

}

void uart_Handler() {
    UART1_ICR_R |= 0b010000;
    uartEvent = 1;
}


void uart_sendChar(char data){
	while ((UART1_FR_R & 0x80) == 0 );
	UART1_DR_R = data;
}

char uart_receive(void){
	//unsigned int dataBuffer;
	char data;

	if((UART1_FR_R & 0x40) != 0){
	data = (char)(UART1_DR_R & 0xFF);
	return data;
	}
	return 0;
}

void uart_sendStr(const char *data){
    while(*data) {
        uart_sendChar(*data);
        data++;
    }
}


