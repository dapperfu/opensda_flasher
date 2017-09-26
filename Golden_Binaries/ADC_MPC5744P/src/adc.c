/*
 * adc.c
 *
 *  Created on: Mar 3, 2016
 *      Author: B55457
 */


#include "adc.h"

#define ADC_VREF  3300 /* ADC ref voltage for both ADC modules. 3300mv or 5000mv */
uint16_t Result[3];     /* ADC channel conversion results */
uint16_t ResultInMv[3]; /* ADC channel conversion results in mv */

void ADC1_PadConfig_ChanSelect(void) { /* Config ADC pads & select scan chans */
     /* Note:  MSCR.SSS configuration  is not needed for inputs if there is  */
     /*        no SSS value is in signal spreadsheet */
     /* Note:  ADC1 Channel 6 on PE12 is connected to XDEVKIT-MPC5744P potentiometer. */

	SIUL2.MSCR[PE12].B.APC = 1; //Configure ADC1_AN6 to analog pad control function. Analog is default function so SSS says 0

	ADC_1.NCMR0.B.CH6 = 1; //Enable channel 6 for normal conversion on ADC1
}

void ADC1_Calibration(void) {       /* Steps below are from reference manual */
  uint32_t ADC1_Calibration_Failed = 1;    /* Calibration has not passed yet */

  ADC_1.MCR.B.PWDN = 1;     /* Power down for starting calibration process */
  ADC_1.MCR.B.ADCLKSEL = 0; /* ADC clock = bus clock/2 (80/2 MHz FS80) */
        /* Note: Calibration requires it to be set at max 40MHz for best results */
  ADC_1.CALBISTREG.B.TEST_EN = 1;       /* Enable calibration test */
  ADC_1.MCR.B.PWDN = 0;     /* Power back up for calibration test to start */
  while(ADC_1.CALBISTREG.B.C_T_BUSY);  /* Wait for calibration to finish */
  if(ADC_1.MSR.B.CALIBRTD) {            /* If calibration ran successfully */
    ADC1_Calibration_Failed = 0;        /* Calibration was successful */
  }
  else  {
    ADC1_Calibration_Failed = 1;        /* Calibration was not successful */
  }

  if(ADC1_Calibration_Failed){} //Functionally useless statement to make compiler happy

}

void ADC1_Init(void) {
  ADC_1.MCR.B.PWDN     = 1;  /* Power down for starting module initialization */
  ADC_1.MCR.B.OWREN    = 1;  /* Enable overwriting older conversion results */
  ADC_1.MCR.B.MODE     = 1;  /* Scan mode (1) used instead of one shot mode */
  ADC_1.MCR.B.ADCLKSEL = 1;  /* ADC clock = FS80 bus clock (80 MHz here) */
  ADC_1.MCR.B.PWDN   = 0;    /* ADC_1 ready to receive converstion triggers */
  ADC_1.MCR.B.NSTART = 1;    /* Initiate trigger for normal scan */
}

void ADC1_Read_Chan (void) {
	Result[0] = ADC_1.CDR[6].B.CDATA; //Read ADC1_AN6 conversion result data
	ResultInMv[0] = (uint16_t) (ADC_VREF*Result[0]/0xFFF); /* Conversion in mv */
}
