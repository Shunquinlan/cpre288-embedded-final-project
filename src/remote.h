// remote.h
// Header file for IR receiver functionality
// Supports 38 kHz IR receiver on PB2

#ifndef REMOTE_H_
#define REMOTE_H_

#include <stdint.h>
#include <stdbool.h>

/**
 * Initialize the IR receiver on PB2
 * Configures Port B clock and sets PB2 as digital input
 */
void ir_recv_init(void);

/**
 * Check if IR signal is detected
 * @return true if IR is present (active-LOW), false otherwise
 */
bool ir_recv_seen(void);

#endif /* REMOTE_H_ */
