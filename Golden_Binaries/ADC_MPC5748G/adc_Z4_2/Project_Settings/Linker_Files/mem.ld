/* Entry Point */
ENTRY(_start)

/* define heap and stack size */
__HEAP_SIZE            = 0 ;
__STACK_SIZE           = 4096 ;

SRAM_SIZE =  256K;    
/* Define SRAM Base Address */
SRAM_BASE_ADDR = 0x40040000;
    
MEMORY
{

    flash_rchw : org = 0x00FA0000,   len = 0x4
    cpu0_reset_vec : org = 0x00FA0000+0x10,   len = 0x4
    cpu1_reset_vec : org = 0x00FA0000+0x14,   len = 0x4
    cpu2_reset_vec : org = 0x00FA0000+0x04,   len = 0x4      
        
    m_text :	org = 0x11d0000, len = 1856K  
    m_data :	org = 0x40040000,   len = 256K
}

