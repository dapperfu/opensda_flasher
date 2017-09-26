/*
 * main implementation: use this 'C' sample to create your own application
 *
 */

#include "derivative.h" /* include peripheral declarations */

extern void xcptn_xmpl(void);

__attribute__ ((section(".text")))
int main(void)
{
	int counter = 0;
	
	xcptn_xmpl ();              /* Configure and Enable Interrupts */

	for(;;) {	   
	   	counter++;
	}
	
	return 0;
}
