.extern main
.text
.globl _start
_start:
    # Config direct window and set PG
    li.w    $t0, 0xa0000011
    csrwr   $t0, 0x180
    /* CSR_DMWIN0(0x180): 0xa0000000-0xbfffffff->0x00000000-0x1fffffff Cached */
    li.w    $t0, 0x80000001
    /* CSR_DMWIN1(0x181): 0x80000000-0x9fffffff->0x00000000-0x1fffffff Uncached */
    # Enable PG
    li.w    $t0, 0xb0
    csrwr   $t0, 0x0
    /* CSR_CRMD(0x0): PLV=0, IE=0, PG */
    la  $sp, bootstacktop
    la  $t0, main
    jr  $t0
poweroff:
    b poweroff
_stack:
.section .data
    .global bootstack
bootstack:
    .space 1024
    .global bootstacktop
bootstacktop:
    .space 64
