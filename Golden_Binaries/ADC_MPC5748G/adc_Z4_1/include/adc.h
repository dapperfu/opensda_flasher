/*
 * adc.h
 *
 *  Created on: Mar 3, 2016
 *      Author: B55457
 */

#ifndef ADC_H_
#define ADC_H_

#include "project.h"

void ADC1_PadConfig_ChanSelect(void);
void ADC1_Calibration(void);
void ADC1_Init (void);
void ADC1_Read_Chan (void);

#endif /* ADC_H_ */
