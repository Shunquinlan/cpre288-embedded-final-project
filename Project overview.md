# Embedded Systems Final Project (CPRE 288)

## Overview
This repository contains the final embedded systems project for **CPRE 288 – Introduction to Embedded Systems** at Iowa State University. The project focuses on low-level C firmware development, real-time behavior, and direct hardware control on an ARM-based microcontroller.

All functionality was implemented using **register-level programming** without high-level abstraction libraries to emphasize microcontroller architecture, peripherals, and timing constraints.

---

## Hardware & Tools
- **Microcontroller:** TM4C123 (ARM Cortex-M4)
- **IDE:** Code Composer Studio
- **Peripherals:** GPIO, Timers (PWM & input capture), ADC, UART, NVIC interrupts

---

## System Capabilities
- Digital and peripheral I/O using GPIO and pin multiplexing  
- Timer-driven control for periodic tasks and PWM generation  
- Analog sensor input via ADC sampling  
- Serial communication using UART for debugging and data output  
- Interrupt-driven execution for responsive real-time behavior  

---

## Software Design
The firmware is written in C and organized around:
- Hardware and peripheral initialization  
- Real-time execution logic  
- Interrupt service routines (ISRs)  

The system was developed directly from the microcontroller datasheet and reference manual to ensure precise hardware control.

---

## Project Results – ProtoCue
The final prototype, **ProtoCue**, demonstrates a real-time, sensor-driven embedded system.

**Results:**
- Integrated multiple sensors with reliable real-time data acquisition  
- Achieved stable timing behavior using hardware timers and interrupts  
- Improved responsiveness through interrupt-based execution compared to polling  
- Successfully validated functionality through repeated live demonstrations  

ProtoCue met all core functional requirements and serves as a proof-of-concept for low-level embedded system design.

---

## Demo & Documentation
- Demo videos are available in the `media/` directory  
- The final project report is available in the `docs/` directory  

---

## Author
**Shun Quinlan**  
Electrical Engineering – Embedded Systems  
Iowa State University
