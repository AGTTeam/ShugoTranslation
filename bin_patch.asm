.nds

.open "ShugoData/repack/arm9.bin",0x021d1000 - 0x938c0 ;fix first value is wrong
  .orga 0x938c0
  .area 0x300

  ;ASCII to SJIS lookup table, also includes VWF values
  SJIS_LOOKUP:
  .import "ShugoData/fontdata.bin"
  .align

  IS_ASCII:
  .dw 0
  VWF_LEN:
  .dw 0

  ;r0=
  CHECK_ASCII:

  LOAD_ASCII:
  ;r1=character to convert
  ;r0 = r1 & 0xff
  ;r2=other character if this is s-sjis
  ;r4=str pointer
  ;r9=str index
  push {r3-r4}
  cmp r0,0x7f
  bgt @@sjis
  ;If the character is ascii, convert it to sjis
  ldr r3,=SJIS_LOOKUP
  sub r4,r0,0x20
  lsl r4,r4,0x2
  add r3,r3,r4
  ldrb r1,[r3]
  and r0,r1,0xff
  ldrb r2,[r3,0x1]
  ldrb r4,[r3,0x2]
  ;Save the VWF value and set IS_ASCII to 1
  ldr r3,=IS_ASCII
  str r4,[r3,0x4]
  mov r4,1
  str r4,[r3]
  b @@ret
  @@sjis:
  ;Set IS_ASCII to 0, set vwf value to the fixed value and return
  ldr r3,=IS_ASCII
  mov r4,0
  str r4,[r3]
  mov r4,0xe
  str r4,[r3,0x4]
  @@ret:
  pop {r3-r4}
  mov r0,r1,lsl 0x10
  bx lr
  .pool

  ;Same as above but r0/r1 are the characters and we just need to convert
  LOAD_ASCII2:
  push {r3-r5}
  and r5,r0,0xff
  cmp r5,0x7f
  bgt @@ret
  ldr r3,=SJIS_LOOKUP
  sub r4,r5,0x20
  lsl r4,r4,0x2
  add r3,r3,r4
  ldrb r0,[r3]
  ldrb r1,[r3,0x1]
  @@ret:
  pop {r3-r5}
  mov r0,r0,lsl 0x10
  bx lr
  .pool

  ADVANCE_SCRIPT:
  push {r0-r1}
  ldr r0,=IS_ASCII
  ldr r1,[r0]
  cmp r1,1
  addne r9,r9,0x2
  addeq r9,r9,0x1
  mov r1,0
  str r1,[r0]
  pop {r0-r1}
  bx lr
  .pool

  VWF:
  push {r0}
  ldr r0,=VWF_LEN
  ldr r0,[r0]
  add r1,r1,r0
  pop {r0}
  bx lr
  .pool
  .endarea
.close

.open "ShugoData/repack/arm9.bin",0x02000000
  ;Don't skip ASCII characters
  .org 0x0203592c
  ;bcc 0x02035a7c
  nop
  .skip 8
  ;mov r0,r1,lsl 0x10
  ;Jump here to convert character to SJIS
  bl LOAD_ASCII

  .org 0x02035994
  ;mov r0,r0,lsl 0x10
  bl LOAD_ASCII2

  ;Check how much we need to advance
  .org 0x02035a74
  ;add r9,r9,0x2
  bl ADVANCE_SCRIPT

  ;Add vwf value
  .org 0x02035a68
  ;add r1,r1,0xe
  bl VWF
.close
