/**************************************************************************/
/*                                                                        */
/* DESCRIPTION:                                                           */
/* This is a generic base template for all core exceptions, excluding     */
/* IVOR4 exceptions which have seperate handler                           */
/*                                                                        */
/* This file starts in memory at the beginning of the                     */
/*".core_exceptions_table_c2" section.                                    */
/**************************************************************************/
#define PPCASM   __asm__
#define PPCASM_STR(x) #x
#define PPCASMF(x) PPCASM (" " PPCASM_STR(x) " ")
#define PPCASMF2(x,x1) PPCASM (" " PPCASM_STR(x) "," PPCASM_STR(x1) " ")

PPCASMF( .globl VTABLE );
PPCASMF( .globl IVOR0_Vector );
PPCASMF( .globl IVOR1_Vector );
PPCASMF( .globl IVOR2_Vector );
PPCASMF( .globl IVOR3_Vector );
PPCASMF( .globl IVOR4_Vector );
PPCASMF( .globl IVOR5_Vector );
PPCASMF( .globl IVOR6_Vector );
PPCASMF( .globl IVOR7_Vector );
PPCASMF( .globl IVOR8_Vector );
PPCASMF( .globl IVOR9_Vector );
PPCASMF( .globl IVOR10_Vector );
PPCASMF( .globl IVOR11_Vector );
PPCASMF( .globl IVOR12_Vector );
PPCASMF( .globl IVOR13_Vector );
PPCASMF( .globl IVOR14_Vector );
PPCASMF( .globl IVOR15_Vector );

PPCASMF( .extern     IVOR4_Handler);
PPCASMF2( .section    .core_exceptions_table, "ax" );

PPCASMF(.align 4);
PPCASMF( VTABLE: );
PPCASMF( IVOR0_Vector: );
PPCASMF( e_b   IVOR0_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR1_Vector: );
PPCASMF( e_b   IVOR1_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR2_Vector: );
PPCASMF( e_b   IVOR2_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR3_Vector: );
PPCASMF( e_b   IVOR3_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR4_Vector: );
PPCASMF( e_b   IVOR4_Handler );

PPCASMF(.align 4);
PPCASMF( IVOR5_Vector: );
PPCASMF( e_b   IVOR5_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR6_Vector: );
PPCASMF( e_b   IVOR6_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR7_Vector: );
PPCASMF( e_b   IVOR7_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR8_Vector: );
PPCASMF( e_b   IVOR8_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR9_Vector: );
PPCASMF( e_b   IVOR9_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR10_Vector: );
PPCASMF( e_b   IVOR10_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR11_Vector: );
PPCASMF( e_b   IVOR11_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR12_Vector: );
PPCASMF( e_b   IVOR12_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR13_Vector: );
PPCASMF( e_b   IVOR13_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR14_Vector: );
PPCASMF( e_b   IVOR14_Vector );

PPCASMF(.align 4);
PPCASMF( IVOR15_Vector: );
PPCASMF( e_b   IVOR15_Vector );


