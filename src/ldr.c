#include <stdio.h>
#include <stdint.h>
#include "../inc/ldr.h"
#include "../inc/tm4c123gh6pm.h"

// ========== LDR helper (PE4 / AIN9 on ADC1) ==========
// Uses your calibration runs to roughly classify:
//   - DARK_TAPE  (black electrical tape on PVC)
//   - PLAIN_PVC  (bright PVC)
//   - UNKNOWN    (overlap zone)

typedef enum {
    LDR_UNKNOWN = 0,
    LDR_DARK_TAPE,
    LDR_PLAIN_PVC
} ldr_class_t;

// Raw thresholds from your data (tunable)
#define LDR_DARK_MAX_RAW     2860  // below this: very likely black tape (close)
#define LDR_PLAIN_MIN_RAW    2865  // above this: very likely plain PVC (close)

// LDR on PE4 (AIN9), using ADC1 SS3
static void ldr_gui_init(void)
{
    // 1) Enable Port E clock and ADC1 clock
    SYSCTL_RCGCGPIO_R |= SYSCTL_RCGCGPIO_R4;    // Port E
    SYSCTL_RCGCADC_R  |= SYSCTL_RCGCADC_R1;     // ADC1

    volatile int delay = SYSCTL_RCGCGPIO_R;     // small delay
    (void)delay;

    // 2) Configure PE4 as analog input
    GPIO_PORTE_AFSEL_R |= (1 << 4);    // alternate function on PE4
    GPIO_PORTE_DEN_R   &= ~(1 << 4);   // disable digital
    GPIO_PORTE_AMSEL_R |= (1 << 4);    // enable analog

    // 3) Configure ADC1 SS3 for AIN9, software trigger
    ADC1_ACTSS_R &= ~ADC_ACTSS_ASEN3;        // disable SS3 during config
    ADC1_EMUX_R  &= ~ADC_EMUX_EM3_M;         // EM3 = 0 -> software trigger
    ADC1_SSMUX3_R = 9;                       // channel 9 = AIN9 (PE4)
    ADC1_SSCTL3_R = ADC_SSCTL3_IE0 |         // interrupt enable
                    ADC_SSCTL3_END0;         // single sample, end of seq
    ADC1_ACTSS_R |= ADC_ACTSS_ASEN3;         // re-enable SS3
}

// Public initialization function
void ldr_init(void)
{
    ldr_gui_init();
}

// One raw ADC reading (0–4095)
static uint16_t ldr_read_raw_gui(void)
{
    ADC1_PSSI_R |= ADC_PSSI_SS3;                 // start conversion on SS3
    while ((ADC1_RIS_R & ADC_RIS_INR3) == 0) {   // wait complete
        // spin
    }
    uint16_t result = ADC1_SSFIFO3_R & 0x0FFF;   // 12-bit result
    ADC1_ISC_R = ADC_ISC_IN3;                    // clear flag
    return result;
}

// Public function to read raw ADC value
uint16_t ldr_read_raw(void)
{
    return ldr_read_raw_gui();
}

static ldr_class_t ldr_classify(uint16_t raw)
{
    if (raw < LDR_DARK_MAX_RAW) {
        return LDR_DARK_TAPE;    // clearly darker than PVC in your tests
    } else if (raw > LDR_PLAIN_MIN_RAW) {
        return LDR_PLAIN_PVC;    // clearly brighter than black tape
    } else {
        return LDR_UNKNOWN;      // overlap / far range
    }
}

static const char *ldr_class_name(ldr_class_t c)
{
    switch (c) {
    case LDR_DARK_TAPE:  return "DARK_TAPE";
    case LDR_PLAIN_PVC:  return "PLAIN_PVC";
    default:             return "UNKNOWN";
    }
}

// Public function to detect and classify surface
uint8_t ldr_detect_surface(void)
{
    uint16_t raw = ldr_read_raw();
    ldr_class_t classification = ldr_classify(raw);
    return (uint8_t)classification;
}

// Public function to get surface name
const char* ldr_get_surface_name(uint8_t surface_type)
{
    return ldr_class_name((ldr_class_t)surface_type);
}
