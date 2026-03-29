/**
 *
 * Shawn R. -- V0: 11/12/25 - 11/14/25
 *
 *             V1: 11/18/25 --> just added a setter for the threshold 
 *
 * these sensors return a binary 0 = no cliff 1= cliff
 *  self->cliffLeft = packet[2];
    self->cliffFrontLeft = packet[3];
    self->cliffFrontRight = packet[4];
    self->cliffRight = packet[5];
 *
 *  these sensors return an unsigned 16-bit value that measures the "strength" of the signal
 *
 *  --Jesse recommends using the signal values over the binary values, but I'll keep both here just in case

    self->cliffLeftSignal = oi_parseInt(packet + 28);
    self->cliffFrontLeftSignal = oi_parseInt(packet + 30);
    self->cliffFrontRightSignal = oi_parseInt(packet + 32);
    self->cliffRightSignal = oi_parseInt(packet + 34);
 *
 *
 */

#ifndef CLIFF_H_
#define CLIFF_H_

#include "lcd.h"
#include "open_interface.h"


//manually change the cliff threshold -- otherwise set to be 2000 by default
void set_cliff_threshold(int threshold);

//boolean check for right and left cliffs -- in V0: only using front left and front right
char cliff_found(oi_t *sensor);

/*
 * displays the four cliff sensor 16-bit values onto the lcd screen
 *
 *
 */
void read_cliffs(oi_t *sensor);



/**
 * A simple move_forward() program that shows the cliff detection working as intended
 * When this gets incorporated into the larger project, "cliff" will just be responsible
 * for cliffs and not stopping the wheels, I imagine, but this is a
 * helpful sanity check in the meantime
 *
 * -- Move forward 1 m , 200 wheel speed, until cliff detected
 */
void stop_at_cliffs_sample_program(oi_t *sensor);

//returns the number of cliffs (scans above CLIFF_THRESHOLD) were encountered while running read_cliffs();
int get_cliff_count();

//a first attempt at the protocol which will help our bot leave the test field after successfully getting to its destination
//the real version should probably live within movement.c when it's all said and done
void exit_testfield();

#endif
