/*****************************************************************************/
/* FILE NAME: mode.c                  COPYRIGHT (c) NXP Semiconductors 2016  */
/*                                                      All Rights Reserved  */
/* DESCRIPTION:  Clock mode entry functions.                                 */
/*                                                                           */
/*****************************************************************************/
/* REV      AUTHOR              DATE        DESCRIPTION OF CHANGE            */
/* ---   -----------          ----------    ---------------------            */
/* 1.0	  MS		          11 Jul 2013   Initial working version          */
/* 1.1    S Mihalik			  11 Sep 2013   Added mode verfication after mode*/
/*                    		  transition, added comments and deleted unused  */
/* 							  functions 									 */
/* 1.2	  S Mihalik			  08 Oct 2013   Re-organization,minor code change*/
/* 1.3    S Mihalik  		  13 Nov 2013   Replaced "while" with "if" clause*/
/* 							  in mode verification 							 */
/* 1.4    S Mihalik           29 Jan 2015   Removed code: writes to SC_DC3,  */
/* 							  SC_DC4 (caused IVOR1) & changed PLLCAL3,		 */
/*                       	  init order of PREDIV, MFD, RFDPHI 			 */
/* 1.5	  K Shah			  25 Feb 2016   Code ported to S32DS			 */
/*****************************************************************************/

#include "project.h"


//This changes the mode from 16MHz internal to 160MHz PLL.
void PLL_160MHz(void)
{
  /* Connect XOSC to PLL */
  MC_CGM.AC5_SC.B.SELCTL=1;

  /* Configure PLL0 Dividers - 160MHz from 40Mhx XOSC */
  /* PLL input = FXOSC = 40MHz
     VCO range = 600-1200MHz
  */
  PLLDIG.PLLDV.B.PREDIV  = 1; 	/* Divide input clock by 1, resulting clock will be reference input for the PLL analog loop */
  PLLDIG.PLLDV.B.MFD     = 16; 	/* Loop multiplication factor 16*40 MHz */
  PLLDIG.PLLDV.B.RFDPHI  = 1; 	/* VCO post divider = 4 so 16*40/40 = 160MHz */

  PLLDIG.PLLCAL3.R = 0x09C3C000; /* Contains the denominator of the fractional loop division factor */
  	  	  	  	  	  	  	  	 /* MFDEN = 9C3C000h = 163823616 */
  PLLDIG.PLLFD.B.SMDEN = 1;		 /* Sigma delta modulation enabled */
  /* switch to PLL */
  MC_ME.DRUN_MC.R = 0x00130072;	/* MVRON = 1, FLAON = RUN mode, PLLON=1, FXOSCON = 1, FIRCON = 1, SYSCLK = PLL PHI_0 */
  MC_ME.MCTL.R = 0x30005AF0; 	/* Target mode = DRUN, KEY = 5AF0 */
  MC_ME.MCTL.R = 0x3000A50F; 	/* Target mode = DRUN, KEY = A50F */

  while(MC_ME.GS.B.S_MTRANS == 1);      /* Wait for mode transition complete */
}

void system160mhz(void)
{
  /* F160 - max 160 MHz */
  MC_CGM.SC_DC0.B.DIV = 0;  /* Freq = sysclk / (0+1) = sysclk */
  MC_CGM.SC_DC0.B.DE  = 1;  /* Enable divided clock */

  /* S80 - max 80 MHz */
  /* MC_CGM_SC_DC1[DIV] and MC_CGM_SC_DC5[DIV] must be equal at all times */
  MC_CGM.SC_DC1.B.DIV = 1;  /* Freq = sysclk / (2+1) = sysclk/2 */
  MC_CGM.SC_DC1.B.DE  = 1;  /* Enable divided clock */

  /* FS80 - max 80 MHz */
  /* MC_CGM_SC_DC1[DIV] and MC_CGM_SC_DC5[DIV] must be equal at all times */
  MC_CGM.SC_DC5.R = MC_CGM.SC_DC1.R;  /* 80 MHz max */

  /* S40 - max 40 MHz */
  MC_CGM.SC_DC2.B.DIV = 3;  /* Freq = sysclk / (3+1) = sysclk/4 */
  MC_CGM.SC_DC2.B.DE  = 1;  /* Enable divided clock */

  /* F40 - max 40 MHz (for PIT, etc.) - use default values */

  /* F80 - max 80 MHz - use default values*/

  /* F20 - clock out configured at clock_out* function */

  PLL_160MHz();
}

void enter_STOP_mode (void) {		/* Transit to STOP mode */
  MC_ME.MCTL.R = 0xA0005AF0;		/* Enter STOP mode and key */
  MC_ME.MCTL.R = 0xA000A50F;		/* Enter STOP mode and inverted key */
  while (MC_ME.GS.B.S_MTRANS) {}	/* Wait for STOP mode transition to complete */
}
