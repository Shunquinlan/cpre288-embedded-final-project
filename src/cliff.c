/**
    Shawn R. -- V0: 11/12/25
*/


/**
 *
 * Shawn R. -- V0: 11/12/25
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
 **/

#include "../inc/cliff.h"
#include "../inc/lcd.h"
#include "../inc/open_interface.h"

//default value for cliff threshold
int CLIFF_THRESHOLD = 2000;
int cliff_count = 0;

//manually change the cliff threshold -- otherwise set to be 2000 by default
void set_cliff_threshold(int threshold){
    CLIFF_THRESHOLD = threshold;
}


//boolean check for right and left cliffs -- in V0: only using front left and front right
char cliff_found(oi_t *sensor){
    unsigned short currL = sensor -> cliffLeftSignal;
    unsigned short currFL = sensor -> cliffFrontLeftSignal;
    unsigned short currFR = sensor -> cliffFrontRightSignal;
    unsigned short currR = sensor -> cliffRightSignal;

//    if(currL >= CLIFF_THRESHOLD || currFL >= CLIFF_THRESHOLD || currFR >= CLIFF_THRESHOLD || currR >= CLIFF_THRESHOLD ){
//        return 1;
//    }

    if(currFL >= CLIFF_THRESHOLD || currFR >= CLIFF_THRESHOLD){
        return 1;
    }
    return 0;
}

/**
 * A simple move_forward() program that shows the cliff detection working as intended
 * When this gets incorporated into the larger project, "cliff" will just be responsible
 * for cliffs and not stopping the wheels, I imagine, but this is a
 * helpful sanity check in the meantime
 *
 * -- Move forward 1 m , 200 wheel speed, until cliff detected
 */
void stop_at_cliffs_sample_program(oi_t *sensor){
        double sum = 0;
        oi_setWheels(200,200);
        char cliff_value = cliff_found(sensor);

        while(sum < 1000 && cliff_value <= 0){
           oi_update(sensor);
           sum += sensor -> distance;
           read_cliffs(sensor);
           cliff_value = cliff_found(sensor);
        }
        
        // Stop the robot when cliff is found or distance reached
        oi_setWheels(0, 0);
        
        lcd_printf("Stopped! Cliffs: %d", get_cliff_count());
}


/*
 * displays the four cliff sensor 16-bit values onto the lcd screen
 *
 *
 */
void read_cliffs(oi_t *sensor){

    unsigned short currL = sensor -> cliffLeftSignal;
    unsigned short currFL = sensor -> cliffFrontLeftSignal;
    unsigned short currFR = sensor -> cliffFrontRightSignal;
    unsigned short currR = sensor -> cliffRightSignal;

    lcd_printf("%hu %hu %hu %hu", currL, currFL, currFR, currR);
    if(cliff_found(sensor) == 1){
        cliff_count++;
    }
}

//returns the number of cliffs (scans above CLIFF_THRESHOLD) were encountered while running read_cliffs();

int get_cliff_count(){
    return cliff_count;
}

//a first attempt at the protocol which will help our bot leave the test field after successfully getting to its destination
//the real version should probably live within movement.c when it's all said and done
void exit_testfield(){
    //disable cliff sensing, maybe by making the threshold really high?
    //can it be made high enough to let you drive through white boundary tape, but not high enough to drive on black ?

    //AUTO
    //-- determine if there is/are boundary(ies) nearby, and if so which one is closest...
    //-- drive to (and through) said boundary without running into obstacles on the way
    //-- "through" could be defined by still recognizing white tape has been crossed, and going an additional n distance after that

}

