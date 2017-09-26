/* main.c - ADC SW Scan example for MPC5744P */
/* Description:  Converts inputs ADC1_AN1 using scan mode (continuous) */
/* Rev 1 Sept 06 2016 D Chung - initial version */
/* Copyright NXP Semiconductor, Inc 2016 All rights reserved. */

/*******************************************************************************
* NXP Semiconductor Inc.
* (c) Copyright 2016 NXP Semiconductor, Inc.
* ALL RIGHTS RESERVED.
********************************************************************************
Services performed by NXP in this matter are performed AS IS and without
any warranty. CUSTOMER retains the final decision relative to the total design
and functionality of the end product. NXP neither guarantees nor will be
held liable by CUSTOMER for the success of this project.
NXP DISCLAIMS ALL WARRANTIES, EXPRESSED, IMPLIED OR STATUTORY INCLUDING,
BUT NOT LIMITED TO, IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR
A PARTICULAR PURPOSE ON ANY HARDWARE, SOFTWARE ORE ADVISE SUPPLIED TO THE PROJECT
BY NXP, AND OR NAY PRODUCT RESULTING FROM NXP SERVICES. IN NO EVENT
SHALL NXP BE LIABLE FOR INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF
THIS AGREEMENT.

CUSTOMER agrees to hold NXP harmless against any and all claims demands or
actions by anyone on account of any damage, or injury, whether commercial,
contractual, or tortuous, rising directly or indirectly as a result of the advise
or assistance supplied CUSTOMER in connection with product, services or goods
supplied under this Agreement.
********************************************************************************
* File              main.c
* Owner             David Chung
* Version           1.0
* Date              Sept-6-2016
* Classification    General Business Information
* Brief             Tests MPC5744P ADC. LEDs turn on/off based on ADC result.
********************************************************************************
* Detailed Description:
* Application performs basic ADC initialization.  ADC scans ADC1_AN6 in
* continuous mode.  The three components of the RGB LED turn on based on ADC result.
*
* ------------------------------------------------------------------------------
* Test HW:         XDEVKIT-MPC5744P
* MCU:             MPC5744P
* Terminal:        None
* Fsys:            160 MHz
* Debugger:        OpenSDA
* Target:          FLASH
* EVB connection:  None
*
********************************************************************************
Revision History:
Version  Date         Author  			Description of Changes
1.0      Sept-06-2016  David Chung	  	Initial version

*******************************************************************************/

#include "derivative.h" /* include peripheral declarations */
#include "project.h"
#include "mode_entry.h"
#include "adc.h"

extern void xcptn_xmpl(void);
void peri_clock_gating(void);  /* Configure gating/enabling peri. clocks */
void LED_Config(void);   /* Assign LED ports on Freescale EVBs as GPIO outputs */
void update_LEDs(void); /* Update LEDs with scaled chan 9 result */
extern uint16_t Result[3];     /* ADC channel conversion results */

__attribute__ ((section(".text")))
int main(void)
{
	int counter = 0;
	
	xcptn_xmpl ();              /* Configure and Enable Interrupts */

	peri_clock_gating();    /* Configure gating/enabling peri. clocks for modes*/
	system160mhz();         /* sysclk=160MHz, dividers configured, mode trans*/

	LED_Config();           /* Assign LED ports on Freescale LED as GPIO outputs*/

	MC_CGM.AC0_SC.B.SELCTL = 0b10; //Select PLL0_PHI as source of ADC analog clock

	MC_CGM.AC0_DC2.R = 0x80040000; //Enable ADC_CLK and divide PLL0_PHI source by 5 (i.e. 4+1)

	ADC1_PadConfig_ChanSelect();  /* Configure ADC pads & select scan channels */
	ADC1_Calibration();     /* Calibrate to compensate for variations */
	ADC1_Init();            /* Initialize ADC1 module & start normal scan mode */

	for(;;) {	   
	   	counter++;
		if (ADC_1.ISR.B.ECH) { /* If normal scan channels finished converting */
		  ADC1_Read_Chan();    /* Read conversion results */
		  update_LEDs();       /* Update LEDs with scaled chan 1 result */
		  ADC_1.ISR.R = 0x00000001; /* Clear End of CHain (ECH) status bit */
		}
	}

	return 0;
}

void peri_clock_gating (void) {
  MC_ME.RUN_PC[0].R = 0x00000000;  /* gate off clock for all RUN modes */
  MC_ME.RUN_PC[1].R = 0x000000FE;  /* enable peri clock for all RUN modes */
                                   /* Note: RUN_PC0 is default cfg for PCTLs */
  MC_ME.PCTL126.B.RUN_CFG = 0x1;
}

void LED_Config(void) {        /* Assign LED ports as GPIO outputs */

	/* Configure the RGB LED on DEVKIT-MPC5744P */
	SIUL2.MSCR[PC11].B.OBE = 1;
	SIUL2.MSCR[PC12].B.OBE = 1;
	SIUL2.MSCR[PC13].B.OBE = 1;

	/* Turn off LEDs. LEDs are active low */
	SIUL2.GPDO[PC11].R = 1;
	SIUL2.GPDO[PC12].R = 1;
	SIUL2.GPDO[PC13].R = 1;

}

void update_LEDs(void) {     /* Update LEDs with scaled chan 6 result  */
                             /* If Result bit is 0, then LED is turned ON */
                             /* If Result bit is 1, then LED is turned OFF */
	SIUL2.GPDO[PC11].R  = (Result[0] & 0x0800)>>11; /* LED1: scaled ch 6 LSB */
	SIUL2.GPDO[PC12].R  = (Result[0] & 0x0400)>>10; /* LED2 */
	SIUL2.GPDO[PC13].R = (Result[0] & 0x0200)>>9;  /* LED3 */

}
