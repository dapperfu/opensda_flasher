################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.local

# Add inputs and outputs from these tool invocations to the build variables 
S_UPPER_SRCS_QUOTED += \
"../src/intc_sw_handlers.S" \

C_SRCS_QUOTED += \
"../src/MPC57xx__Interrupt_Init.c" \
"../src/Vector.c" \
"../src/adc_Z4_2.c" \
"../src/intc_SW_mode_isr_vectors_MPC5748G.c" \

S_UPPER_SRCS += \
../src/intc_sw_handlers.S \

C_SRCS += \
../src/MPC57xx__Interrupt_Init.c \
../src/Vector.c \
../src/adc_Z4_2.c \
../src/intc_SW_mode_isr_vectors_MPC5748G.c \

OBJS_OS_FORMAT += \
./src/MPC57xx__Interrupt_Init.o \
./src/Vector.o \
./src/adc_Z4_2.o \
./src/intc_SW_mode_isr_vectors_MPC5748G.o \
./src/intc_sw_handlers.o \

C_DEPS_QUOTED += \
"./src/MPC57xx__Interrupt_Init.d" \
"./src/Vector.d" \
"./src/adc_Z4_2.d" \
"./src/intc_SW_mode_isr_vectors_MPC5748G.d" \

OBJS += \
./src/MPC57xx__Interrupt_Init.o \
./src/Vector.o \
./src/adc_Z4_2.o \
./src/intc_SW_mode_isr_vectors_MPC5748G.o \
./src/intc_sw_handlers.o \

OBJS_QUOTED += \
"./src/MPC57xx__Interrupt_Init.o" \
"./src/Vector.o" \
"./src/adc_Z4_2.o" \
"./src/intc_SW_mode_isr_vectors_MPC5748G.o" \
"./src/intc_sw_handlers.o" \

C_DEPS += \
./src/MPC57xx__Interrupt_Init.d \
./src/Vector.d \
./src/adc_Z4_2.d \
./src/intc_SW_mode_isr_vectors_MPC5748G.d \


# Each subdirectory must supply rules for building sources it contributes
src/MPC57xx__Interrupt_Init.o: ../src/MPC57xx__Interrupt_Init.c
	@echo 'Building file: $<'
	@echo 'Executing target #1 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	powerpc-eabivle-gcc "@src/MPC57xx__Interrupt_Init.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -c -o "src/MPC57xx__Interrupt_Init.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '

src/Vector.o: ../src/Vector.c
	@echo 'Building file: $<'
	@echo 'Executing target #2 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	powerpc-eabivle-gcc "@src/Vector.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -c -o "src/Vector.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '

src/adc_Z4_2.o: ../src/adc_Z4_2.c
	@echo 'Building file: $<'
	@echo 'Executing target #3 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	powerpc-eabivle-gcc "@src/adc_Z4_2.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -c -o "src/adc_Z4_2.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '

src/intc_SW_mode_isr_vectors_MPC5748G.o: ../src/intc_SW_mode_isr_vectors_MPC5748G.c
	@echo 'Building file: $<'
	@echo 'Executing target #4 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	powerpc-eabivle-gcc "@src/intc_SW_mode_isr_vectors_MPC5748G.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -c -o "src/intc_SW_mode_isr_vectors_MPC5748G.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '

src/intc_sw_handlers.o: ../src/intc_sw_handlers.S
	@echo 'Building file: $<'
	@echo 'Executing target #5 $<'
	@echo 'Invoking: Standard S32DS Assembler'
	powerpc-eabivle-gcc "@src/intc_sw_handlers.args" -c -o "src/intc_sw_handlers.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '


