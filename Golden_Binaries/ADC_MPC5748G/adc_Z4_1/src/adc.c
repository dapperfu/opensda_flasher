/*****************************************************************************/
/* FILE NAME: ADC.c                   COPYRIGHT (c) NXP Semiconductors 2016  */
/*                                                      All Rights Reserved  */
/* PLATFORM: DEVKIT-MPC5748G												 */
/* DESCRIPTION:  ADC module functions.                                       */
/*                                                                           */
/*****************************************************************************/
/* REV      AUTHOR              DATE        DESCRIPTION OF CHANGE            */
/* ---   -----------          ----------    ---------------------            */
/* 1.0	  J Cisneros          29 Jul 2013   Initial working version          */
/* 1.1    S Mihalik/C Hillier 13 Jan 2014   Code modifications               */
/* 1.2	  K Shah			  03 Mar 2016   Code modifications				 */
/*****************************************************************************/

#include "adc.h"

#define ADC_VREF  3300 	/* ADC ref voltage for both ADC modules. 3300mV or 5000mV */
uint16_t Result;     	/* ADC channel conversion results */
uint16_t ResultInMv; 	/* ADC channel conversion results in mV */

void ADC1_PadConfig_ChanSelect(void) {	/* Configure ADC pads & select scan channel */
     	 	 	 	 	 	 	 	 	/* Note:  MSCR.SSS configuration  is not needed for inputs if there is  */
     	 	 	 	 	 	 	 	 	/*        no SSS value is in signal spreadsheet */
     	 	 	 	 	 	 	 	 	/* Note:  ADC1 channel 9 on port PB4 is connected to pot on NXP EVB */
   SIUL2.MSCR[PB4].B.APC = 1;    		/* PB4 = function ADC1_P[0] = ADC 1 channel  9 */
   ADC_1.NCMR0.B.CH9  = 1;   			/* Enable channel  9 for normal conversion on ADC1 */
}

void ADC1_Calibration(void) {       	/* Calibrate to compensate for variations.
 	 	 	 	 	 	 	 	 	 	   Steps below are from reference manual */
  uint32_t __attribute__ ((unused)) ADC1_Calibration_Failed = 1; /* Calibration has not passed yet */

  ADC_1.MCR.B.PWDN = 1;     			/* Power down for starting calibration process */
  ADC_1.MCR.B.ADCLKSEL = 0; 			/* ADC clock = bus clock/2 (80/2 MHz FS80) */
        								/* Note: Calibration requires it to be set at max 40MHz for best results */
  ADC_1.CALBISTREG.B.TEST_EN = 1;      	/* Enable calibration test */
  ADC_1.MCR.B.PWDN = 0;     			/* Power back up for calibration test to start */
  while(ADC_1.CALBISTREG.B.C_T_BUSY);   /* Wait for calibration to finish */
  if(ADC_1.MSR.B.CALIBRTD) {            /* If calibration ran successfully */
    ADC1_Calibration_Failed = 0;        /* Calibration was successful */
  }
  else  {
    ADC1_Calibration_Failed = 1;        /* Calibration was not successful */
  }

}

void ADC1_Init(void) {		 /* Initialize ADC1 module & start normal scan mode */
  ADC_1.MCR.B.PWDN     = 1;  /* Power down for starting module initialization */
  ADC_1.MCR.B.OWREN    = 1;  /* Enable overwriting older conversion results */
  ADC_1.MCR.B.MODE     = 1;  /* Scan mode (1) used instead of one shot mode */
  ADC_1.MCR.B.ADCLKSEL = 1;  /* ADC clock = FS80 bus clock (80 MHz here) */
  ADC_1.MCR.B.PWDN   = 0;    /* ADC_1 ready to receive conversation triggers */
  ADC_1.MCR.B.NSTART = 1;    /* Initiate trigger for normal scan */
}

void ADC1_Read_Chan (void) {						/* Read conversion results */
  Result= ADC_1.CDR[9].B.CDATA;						/* Read channel 9 conversion result data */
  ResultInMv = (uint16_t) (ADC_VREF*Result/0xFFF);	/* Conversion in mV */
}
