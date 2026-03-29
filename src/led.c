#include "../inc/led.h"
#include <stdint.h>
#include "../inc/tm4c123gh6pm.h"

// / ========= LED on Port F (PF1 red, PF3 green) =========
#define LED_RED_MASK    0x02  // PF1
#define LED_GREEN_MASK  0x08  // PF3
#define LED_ALL_MASK    (LED_RED_MASK | LED_GREEN_MASK)

void led_init(void)
{
    // Enable clock to Port F
    SYSCTL_RCGCGPIO_R |= SYSCTL_RCGCGPIO_R5;
    while ((SYSCTL_PRGPIO_R & SYSCTL_PRGPIO_R5) == 0) {
        // wait
    }

    GPIO_PORTF_DIR_R |= LED_ALL_MASK;   // PF1, PF3 outputs
    GPIO_PORTF_DEN_R |= LED_ALL_MASK;   // digital enable
    GPIO_PORTF_DATA_R &= ~LED_ALL_MASK; // all off
}

void led_write(uint8_t mask)
{
    GPIO_PORTF_DATA_R =
        (GPIO_PORTF_DATA_R & ~LED_ALL_MASK) | (mask & LED_ALL_MASK);
}

void led_off(void)          { led_write(0); }
void led_yellow(void)       { led_write(LED_RED_MASK | LED_GREEN_MASK); }
void led_red(void)          { led_write(LED_RED_MASK); }
void led_green(void)        { led_write(LED_GREEN_MASK); }
