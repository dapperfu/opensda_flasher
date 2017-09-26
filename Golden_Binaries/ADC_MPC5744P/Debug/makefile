################################################################################
# Automatically-generated file. Do not edit!
################################################################################

#Progress monitor hint: 9
first : all
-include ../makefile.init

# This file contains definitions of environment variables used in the makefiles and .args files if exist.
-include makefile.local

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include subdir.mk
-include src/subdir.mk
-include Project_Settings/Startup_Code/subdir.mk
-include Project_Settings/Linker_Files/subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
EXECUTABLES += \
ADC_MPC5744P.elf \

EXECUTABLES_QUOTED += \
"ADC_MPC5744P.elf" \

EXECUTABLES_OS_FORMAT += \
ADC_MPC5744P.elf \


# All Target
all: warning-messages explicit-dependencies ADC_MPC5744P.elf secondary-outputs

# Tool invocations
ADC_MPC5744P.elf: $(OBJS) C:/NXP/workspaceS32DS.Power12/ADC_MPC5744P/Project_Settings/Linker_Files/57xx_flash.ld C:/NXP/workspaceS32DS.Power12/ADC_MPC5744P/Project_Settings/Linker_Files/libs.ld $(OSPT) $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Executing target #10 $@'
	@echo 'Invoking: Standard S32DS C Linker'
	powerpc-eabivle-gcc -o "ADC_MPC5744P.elf" "@ADC_MPC5744P.args"  $(USER_OBJS_QUOTED) $(LIBS_QUOTED) $(OSPT)
	@echo 'Finished building target: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) ./*/*.d  ./*/*/*.o ./*/*.o  $(EXECUTABLES_QUOTED)
	-@echo ' '

secondary-outputs:

.PHONY: all clean dependents explicit-dependencies warning-messages
.SECONDARY:

-include ../makefile.targets

explicit-dependencies: 

warning-messages: 

