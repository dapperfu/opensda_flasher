/*****************************************************************************/
/* FILE NAME: 	 adc_Z4_1.c           COPYRIGHT (c) NXP Semiconductors 2016  */
/*                                                      All Rights Reserved  */
/* PLATFORM:	 DEVKIT-MPC5748G											 */
/* DESCRIPTION:  Initializes ADC1_CH9 to read to Potentiometer at PB4.       */
/*               The eight most significant bits read from ADC1_CH9 light up */
/*               LEDs on NXP evaluation board.  ADC1_CH9 is connected 		 */
/*               to a pot on the EVB so turning the pot outputs values 0-0xFF*/
/*                                                                           */
/*****************************************************************************/
/* REV      AUTHOR              DATE        DESCRIPTION OF CHANGE            */
/* ---   -----------          ----------    ---------------------            */
/* 1.0	  J Cisneros          29 Jul 2013   Initial working version          */
/* 1.1    S Mihalik/C Hillier 02 Jan 2014   ADC code modifications           */
/* 1.2    S Mihalik           27 Jan 2015   Moved SWT_disable function to    */
/*                           boot code & removed unrequired SIUL ME_PCTL code*/
/* 1.3	  K Shah			  18 Mar 2016	Ported program to make compatible*/
/* 							 with S32DS & DEVKIT-MPC5748G					 */
/*****************************************************************************/

#include "derivative.h" /* Include peripheral declarations */
#include "project.h"	/* Define Macros */
#include "mode.h"		/* Change clock modes */
#include "adc.h"		/* Configure ADC */

#define KEY_VALUE1 0x5AF0ul
#define KEY_VALUE2 0xA50Ful

extern void xcptn_xmpl(void);	/* Configure and Enable Interrupts */
void peri_clock_gating(void);  	/* Configure gating/enabling peripheral(ADC) clocks */
void LED_Config(void);			/* Assign LED ports on NXP EVB as GPIO outputs */
void update_LEDs(void);			/* Update LEDs with scaled channel 9 Result */
extern uint16_t Result;     	/* ADC channel conversion Results */

void hw_init(void)
{
#if defined(DEBUG_SECONDARY_CORES)
	uint32_t mctl = MC_ME.MCTL.R;
#if defined(TURN_ON_CPU1)
	/* enable core 1 in all modes */
	MC_ME.CCTL[2].R = 0x00FE;
	/* Set Start address for core 1: Will reset and start */
	MC_ME.CADDR[2].R = 0x11d0000 | 0x1;
#endif	
#if defined(TURN_ON_CPU2)
	/* enable core 2 in all modes */
	MC_ME.CCTL[3].R = 0x00FE;
	/* Set Start address for core 2: Will reset and start */
	MC_ME.CADDR[3].R = 0x13a0000 | 0x1;
#endif
	MC_ME.MCTL.R = (mctl & 0xffff0000ul) | KEY_VALUE1;
	MC_ME.MCTL.R =  mctl; /* key value 2 always from MCTL */
#endif /* defined(DEBUG_SECONDARY_CORES) */
}

__attribute__ ((section(".text")))

/************************************ Main ***********************************/

int main(void)
{
	xcptn_xmpl ();          /* Configure and Enable Interrupts */
    peri_clock_gating();    /* Configure gating/enabling peripheral(ADC) clocks */
	system160mhz();         /* Sets clock dividers= max frequency, calls PLL_160MHz function which:
	                		   MC_ME.ME: enables all modes for Mode Entry module
		            		   Connects XOSC to PLL
		            		   PLLDIG: LOLIE=1, PLLCAL3=0x09C3_C000, no sigma-delta, 160MHz
		            		   MC_ME.DRUN_MC: configures sysclk = PLL
		            		   Mode transition: re-enters DRUN mode */
	LED_Config();           /* Assign LED ports on NXP EVB as GPIO outputs*/

	ADC1_PadConfig_ChanSelect();	/* Configure ADC pads & select scan channel */
	ADC1_Calibration();     		/* Calibrate to compensate for variations */
	ADC1_Init();            		/* Initialize ADC1 module & start normal scan mode */

	while(1) {
	  if (ADC_1.ISR.B.ECH) { 		/* If normal scan channels finished converting */
	    ADC1_Read_Chan();    		/* Read conversion Results */
	    update_LEDs();       		/* Update LEDs with channel 9 Results */
	    ADC_1.ISR.R = 0x00000001;	/* Clear End of CHain (ECH) status bit */
	  }
	}
	
	return 0;
}

/********************  End of Main ***************************************/

void peri_clock_gating (void) {	   /* Configure gating/enabling peripheral(ADC) clocks */
  MC_ME.RUN_PC[0].R = 0x00000000;  /* Gate off clock for all RUN modes */
  MC_ME.RUN_PC[1].R = 0x000000FE;  /* Enable peripheral clock for all RUN modes */
                                   /* Note: RUN_PC0 is default configured for PCTLs */
  MC_ME.PCTL[25].B.RUN_CFG = 0x1;  /* ADC1: Select peripheral configuration RUN_PC[1] */
}

void LED_Config(void) {   /* Assign LED ports on NXP EVB as GPIO outputs */
  SIUL2.GPDO[PA4].R = 1;  /* LED1 Initial value: 1 = LED off on NXP EVB */
  SIUL2.GPDO[PA0].R = 1;  /* LED2 Initial value: 1 = LED off on NXP EVB */
  SIUL2.GPDO[PJ4].R = 1;  /* LED3 Initial value: 1 = LED off on NXP EVB */
  SIUL2.GPDO[PH5].R = 1;  /* LED4 Initial value: 1 = LED off on NXP EVB */
  SIUL2.GPDO[PC4].R = 1;  /* LED5 Initial value: 1 = LED off on NXP EVB */
  SIUL2.GPDO[PH13].R = 1; /* LED6 Initial value: 1 = LED off on NXP EVB */
  SIUL2.GPDO[PA7].R = 1;  /* LED7 Initial value: 1 = LED off on NXP EVB */
  SIUL2.GPDO[PA10].R = 1; /* LED8 Initial value: 1 = LED off on NXP EVB */

  SIUL2.MSCR[PA4].B.OBE = 1;   /* Port PA4 - LED 1 on NXP EVB */
  SIUL2.MSCR[PA0].B.OBE = 1;   /* Port PA0 - LED 2 on NXP EVB  */
  SIUL2.MSCR[PJ4].B.OBE = 1;   /* Port PJ4 - LED 3 on NXP EVB  */
  SIUL2.MSCR[PH5].B.OBE = 1;   /* Port PH5 - LED 4 on NXP EVB  */
  SIUL2.MSCR[PC4].B.OBE = 1;   /* Port PC2 - LED 5 on NXP EVB */
  SIUL2.MSCR[PH13].B.OBE = 1;  /* Port PF15 - LED 6 on NXP EVB  */
  SIUL2.MSCR[PA7].B.OBE = 1;   /* Port PGA7 - LED 7 on NXP EVB  */
  SIUL2.MSCR[PA10].B.OBE = 1;  /* Port PA10 - LED 8 on NXP EVB  */

}

void update_LEDs(void) {     /* Update LEDs with scaled channel 9 Result  */
                             /* If Result bit is 0, then LED is turned ON */
                             /* If Result bit is 1, then LED is turned OFF */
    SIUL2.GPDO[PA4].R  = ~(Result & 0x0800)>>11;/* LED1: scaled channel 9 LSB */
    SIUL2.GPDO[PA0].R  = ~(Result & 0x0400)>>10;/* LED2 */
    SIUL2.GPDO[PJ4].R = ~(Result & 0x0200)>>9;  /* LED3 */
    SIUL2.GPDO[PH5].R = ~(Result & 0x0100)>>8;  /* LED4 */
    SIUL2.GPDO[PC4].R  = ~(Result & 0x0080)>>7; /* LED5 */
    SIUL2.GPDO[PH13].R  = ~(Result & 0x0040)>>6;/* LED6 */
    SIUL2.GPDO[PA7].R = ~(Result & 0x0020)>>5;  /* LED7 */
    SIUL2.GPDO[PA10].R = ~(Result & 0x0010)>>4; /* LED8: scaled channel 9 MSB */
}
