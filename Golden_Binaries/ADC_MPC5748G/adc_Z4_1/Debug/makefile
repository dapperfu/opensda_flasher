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
adc_Z4_1.elf \

EXECUTABLES_QUOTED += \
"adc_Z4_1.elf" \

EXECUTABLES_OS_FORMAT += \
adc_Z4_1.elf \


# All Target
all: warning-messages explicit-dependencies adc_Z4_1.elf secondary-outputs

dependents:
	-cd "C:\NXP\workspaceS32DS.Power12\adc\adc_Z4_2\Debug" && $(MAKE) clean all
	-cd "C:\NXP\workspaceS32DS.Power12\adc\adc_Z2_3\Debug" && $(MAKE) clean all

# Tool invocations
adc_Z4_1.elf: $(OBJS) C:/NXP/workspaceS32DS.Power12/adc/adc_Z4_1/Project_Settings/Linker_Files/mem.ld C:/NXP/workspaceS32DS.Power12/adc/adc_Z4_1/Project_Settings/Linker_Files/sections.ld C:/NXP/workspaceS32DS.Power12/adc/adc_Z4_1/Project_Settings/Linker_Files/libs.ld $(OSPT) $(USER_OBJS) C:/NXP/workspaceS32DS.Power12/adc/adc_Z4_2/Debug/adc_Z4_2.elf C:/NXP/workspaceS32DS.Power12/adc/adc_Z2_3/Debug/adc_Z2_3.elf
	@echo 'Building target: $@'
	@echo 'Executing target #10 $@'
	@echo 'Invoking: Standard S32DS C Linker'
	powerpc-eabivle-gcc -o "adc_Z4_1.elf" "@adc_Z4_1.args"  $(USER_OBJS_QUOTED) $(LIBS_QUOTED) $(OSPT)
	@echo 'Finished building target: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) ./*/*.d  ./*/*/*.o ./*/*.o  $(EXECUTABLES_QUOTED)
	-@echo ' '

secondary-outputs:

.PHONY: all clean dependents explicit-dependencies warning-messages
.SECONDARY:
C:/NXP/workspaceS32DS.Power12/adc/adc_Z4_2/Debug/adc_Z4_2.elf:
C:/NXP/workspaceS32DS.Power12/adc/adc_Z2_3/Debug/adc_Z2_3.elf:

-include ../makefile.targets

explicit-dependencies: 

warning-messages: 

