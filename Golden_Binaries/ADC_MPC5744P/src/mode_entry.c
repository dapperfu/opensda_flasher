/* Rev Jul 11 2013 MS Initial version */
/* Rev Sep 11 2013 SM Added mode verfication after mode transition,  */
/*                    added comments and deleted unused functions */
/* Rev Oct 08 2013 SM Re-organized code and minor code changes */
/* Rev Nov 13 2013 SM Replaced "while" with "if" clause in mode verification */
/* Rev Jan 29 2015 SM Removed code: writes to SC_DC3, SC_DC4 (caused IVOR1)  */
/*                    & changed PLLCAL3, init order of PREDIV, MFD, RFDPHI */

#include "project.h"

void PLL_160MHz(void)
{
  /* Connect XOSC to PLL. We ultimately use the output of PLL1. PLL1 must be fed the output of PLL0 */
  MC_CGM.AC3_SC.B.SELCTL = 1; //40 MHz XOSC selected as input of PLL0

  MC_CGM.AC4_SC.B.SELCTL=0b11; //PLL0_PHI1 selected as input of PHI1

  /* Configure PLL0 Dividers - 160MHz from 40Mhx XOSC */
  /* PLL input = FXOSC = 40MHz
     VCO range = 600-1200MHz
     MPC5744P uses PLL1 for fractional divide options.
     Configure PLL1 first, because it depends on PLL0. So configure while
     PLL0 still off
  */

  /* Program PLL1 to same frequency as PLL0.
   * MFD multiplies input by at least 10. So multiply by 10 and divide by 10.
   * 10/10 = 1, so same frequency as PLL0
   */
  PLLDIG.PLL1DV.B.RFDPHI = 10;
  PLLDIG.PLL1DV.B.MFD = 10;

  /* Configure PLL0 to 160 MHz. */
  PLLDIG.PLL0DV.B.RFDPHI1 = 4;
  PLLDIG.PLL0DV.B.RFDPHI = 4;
  PLLDIG.PLL0DV.B.PREDIV  = 1;
  PLLDIG.PLL0DV.B.MFD     = 16;

  /* switch to PLL */
  MC_ME.DRUN_MC.R = 0x00130072;
  MC_ME.MCTL.R = 0x30005AF0;
  MC_ME.MCTL.R = 0x3000A50F;
  while(MC_ME.GS.B.S_MTRANS == 1);      /* Wait for mode transition complete */
}

void system160mhz(void)
{
	/* PBRIDGEx_CLK */
  MC_CGM.SC_DC0.B.DIV = 3;  /* Freq = sysclk / (0+1) = sysclk */
  MC_CGM.SC_DC0.B.DE  = 1;  /* Enable divided clock */

  PLL_160MHz();
}

void enter_STOP_mode (void) {
  MC_ME.MCTL.R = 0xA0005AF0;      /* Enter STOP mode and key */
  MC_ME.MCTL.R = 0xA000A50F;      /* Enter STOP mode and inverted key */
  while (MC_ME.GS.B.S_MTRANS) {}  /* Wait for STOP mode transition to complete */
}
