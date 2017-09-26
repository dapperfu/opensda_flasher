/**************************************************************************/
/* FILE NAME:                              COPYRIGHT (c) Freescale 2008   */
/* MPC57xx__Interrupt_Init.c                      All Rights Reserved     */
/*                                                                        */
/* DESCRIPTION:                                                           */
/* This is the interrupt controller configuration file.                   */
/*=========================================================================*/
/*                                                                        */
/*========================================================================*/
/* REV      AUTHOR        DATE        DESCRIPTION OF CHANGE               */
/* ---   -----------    ----------    ---------------------               */
/* 0.1    R. Moran       10/12/2008    Initial Version                    */
/**************************************************************************/
#include "derivative.h" /* include peripheral declarations */

#define stringify(s) tostring(s)
#define tostring(s) #s
#define mfspr(rn) ({unsigned int rval; __asm__ volatile("mfspr %0," stringify(rn) : "=r" (rval)); rval;})
#define mtspr(rn, v)   __asm__ volatile("mtspr " stringify(rn) ",%0" : : "r" (v))

#define GetCoreID() ((uint16_t) mfspr(286))

#if defined(MPC574xP) || defined(MPC574xR) || defined(MPC5777M)
#define INTC             INTC_0
#endif

/* Hardware vector mode bit */
#define INTC_BCR_HVEN(coreId)   ( (uint32_t) (0x1UL << ((coreId) << 4UL)) )  /* coreId - hw coreId (value that is read from PIR) */

/*========================================================================*/
/*                      GLOBAL VARIABLES                                  */
/*========================================================================*/
extern const uint32_t IntcIsrVectorTable[];

/*========================================================================*/
/*                      EXTERNAL PROTOTYPES                               */
/*========================================================================*/
extern void VTABLE (void);

/*========================================================================*/
/*                          FUNCTIONS                                     */
/*========================================================================*/
/**************************************************************************/
/* FUNCTION     : SetIVPR                                                 */
/* PURPOSE      : Initialise Core IVPR                                    */
/**************************************************************************/
void SetIVPR (register unsigned int x)
{
	__asm__("mtIVPR %0 \n\t" : : "r"(x));
}

#if defined(MPC5777C)
void InitIVORS (void)
{
    unsigned int reg0, reg1;
    __asm__("e_lis %0, VTABLE@ha \n\t" : "=r" (reg0));
    __asm__("e_add16i %0, %0, VTABLE@l \n\t" : "=r" (reg0));
    __asm__("e_rlwinm %0, %0, 0, 16, 27 \n\t" : "=r" (reg0));
    mtspr(400, reg0);
    __asm__("e_add16i %0, %1, 0x010 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(401, reg1);
    __asm__("e_add16i %0, %1, 0x020 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(402, reg1);
    __asm__("e_add16i %0, %1, 0x030 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(403, reg1);
    __asm__("e_add16i %0, %1, 0x040 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(404, reg1);
    __asm__("e_add16i %0, %1, 0x050 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(405, reg1);
    __asm__("e_add16i %0, %1, 0x060 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(406, reg1);
    __asm__("e_add16i %0, %1, 0x070 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(407, reg1);
    __asm__("e_add16i %0, %1, 0x080 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(408, reg1);
    __asm__("e_add16i %0, %1, 0x090 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(409, reg1);
    __asm__("e_add16i %0, %1, 0x0A0 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(410, reg1);
    __asm__("e_add16i %0, %1, 0x0B0 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(411, reg1);
    __asm__("e_add16i %0, %1, 0x0C0 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(412, reg1);
    __asm__("e_add16i %0, %1, 0x0D0 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(413, reg1);
    __asm__("e_add16i %0, %1, 0x0E0 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(414, reg1);
    __asm__("e_add16i %0, %1, 0x0F0 \n\t" : "=r" (reg1) : "r" (reg0));
    mtspr(415, reg1);
}
#endif

/**************************************************************************/
/* FUNCTION     : InitINTC                                                */
/* PURPOSE      : This function intializes the INTC for software vector   */
/*                mode.                                                   */
/**************************************************************************/
void InitINTC(void) {   

    uint32_t __attribute__((unused)) temp;
#if !defined(MPC574xP)
    uint16_t coreId = GetCoreID ();
#endif

    /* Choose software (HVEN=0) or hardware (HVEN=1) vector mode */
#if defined(MPC574xP)
    INTC.BCR.R   = 0;     /* Software vector mode   */
#elif defined(MPC5777C)
    INTC.MCR.R  &= ~(INTC_BCR_HVEN( coreId ));     /* Software vector mode   */
#else
    INTC.BCR.R  &= ~(INTC_BCR_HVEN( coreId ));     /* Software vector mode   */
#endif
#if defined(MPC574xP)
    temp = INTC.IACKR0.R;
    /* Set INTC ISR vector table base addr. */
    INTC.IACKR0.R = (uint32_t) &IntcIsrVectorTable[0];
#elif defined(MPC5777C)
    temp = INTC.IACKR_PRC[coreId].R;
    /* Set INTC ISR vector table base addr. */
    INTC.IACKR_PRC[coreId].R = (uint32_t) &IntcIsrVectorTable[0];
#else
    temp = INTC.IACKR[coreId].R;
    /* Set INTC ISR vector table base addr. */
    INTC.IACKR[coreId].R = (uint32_t) &IntcIsrVectorTable[0];
#endif
}


/**************************************************************************/
/* FUNCTION     : enableIrq                                               */
/* PURPOSE      : This function sets INTC's current priority to 0.        */
/*                External interrupts to the core are enabled.            */
/**************************************************************************/
void enableIrq(void) {

#if !defined(MPC574xP)
    uint16_t coreId = GetCoreID ();
#endif

    /* Ensure INTC's current priority is 0 */
#if defined(MPC574xP)
    INTC.CPR0.R = 0U;
#elif defined(MPC5777C)
    INTC.CPR_PRC[coreId].R = 0U;
#else
    /* Ensure INTC's current priority is 0 */
    INTC.CPR[coreId].R = 0U;
#endif
    /* Enable external interrupts */
    __asm__(" wrteei 1");
}


/**************************************************************************/
/* FUNCTION     : xcptn_xmpl                                              */
/* PURPOSE      : This function sets up the necessary functions to raise  */
/*                and handle a Interrupt in software vector mode          */
/**************************************************************************/
void xcptn_xmpl(void) {
    
    /* Initialise Core IVPR */
    SetIVPR ((unsigned int) &VTABLE);
#if defined(MPC5777C)
    InitIVORS();
#endif
    /* Initialize INTC for SW vector mode */
    InitINTC();               
    
    /* Enable interrupts */
    enableIrq();

}


