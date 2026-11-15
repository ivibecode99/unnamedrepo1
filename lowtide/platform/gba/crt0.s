@ LOWTIDE GBA startup. ROM header is patched by tools/gbafix.py (logo + checksum).
    .section .crt0, "ax"
    .arm
    .global _start
_start:
    b       1f
    .space  188                 @ logo, title, game code, maker, fixed byte, etc. (0x04..0xBF)
1:
    mov     r0, #0x12           @ IRQ mode
    msr     cpsr_c, r0
    ldr     sp, =0x03007FA0
    mov     r0, #0x1F           @ system mode
    msr     cpsr_c, r0
    ldr     sp, =0x03007E00
    @ copy .data from ROM to IWRAM
    ldr     r0, =__data_load
    ldr     r1, =__data_start
    ldr     r2, =__data_end
2:  cmp     r1, r2
    ldrcc   r3, [r0], #4
    strcc   r3, [r1], #4
    bcc     2b
    @ zero .bss
    ldr     r1, =__bss_start
    ldr     r2, =__bss_end
    mov     r3, #0
3:  cmp     r1, r2
    strcc   r3, [r1], #4
    bcc     3b
    ldr     r0, =main
    bx      r0
    .pool
