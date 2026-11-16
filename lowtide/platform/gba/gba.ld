OUTPUT_ARCH(arm)
ENTRY(_start)
MEMORY {
  rom (rx)  : ORIGIN = 0x08000000, LENGTH = 32M
  iwram (rwx) : ORIGIN = 0x03000000, LENGTH = 31K
}
SECTIONS {
  .text : { KEEP(*(.crt0)) KEEP(*(.sramtag)) *(.text*) *(.rodata*) *(.glue_7) *(.glue_7t) . = ALIGN(4); } > rom
  .data : { __data_start = .; *(.data*) . = ALIGN(4); __data_end = .; } > iwram AT> rom
  __data_load = LOADADDR(.data);
  .bss (NOLOAD) : { . = ALIGN(4); __bss_start = .; *(.bss*) *(COMMON) . = ALIGN(4); __bss_end = .; } > iwram
  .blob : { KEEP(*(.blob*)) } > rom
  /DISCARD/ : { *(.ARM.exidx*) *(.comment) *(.note*) }
}
