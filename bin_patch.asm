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

  ;The amount of characters for each phone key
  .org 0x0208b894
  .db 0x2 ;1
  .db 0x3 ;2
  .db 0x3 ;3
  .db 0x3 ;4
  .db 0x3 ;5
  .db 0x3 ;6
  .db 0x4 ;7
  .db 0x3 ;8
  .db 0x4 ;9
  .db 0x1 ;0

  ;Redefine the characters for each key
  ;no need to change the pointer since there's enough space
  ;1 key
  .org 0x020921e4
  .area 10*2
  .dh 0x8149 ;"！"
  .dh 0x8148 ;"？"
  .endarea
  ;2 key
  .org 0x0209217a
  .area 5*2
  .dh 0x8260 ;"Ａ"
  .dh 0x8261 ;"Ｂ"
  .dh 0x8262 ;"Ｃ"
  .endarea
  ;3 key
  .org 0x02092198
  .area 5*2
  .dh 0x8263 ;"Ｄ"
  .dh 0x8264 ;"Ｅ"
  .dh 0x8265 ;"Ｆ"
  .endarea
  ;4 key
  .org 0x020921cc
  .area 6*2
  .dh 0x8266 ;"Ｇ"
  .dh 0x8267 ;"Ｈ"
  .dh 0x8268 ;"Ｉ"
  .endarea
  ;5 key
  .org 0x02092170
  .area 5*2
  .dh 0x8268 ;"Ｊ"
  .dh 0x826a ;"Ｋ"
  .dh 0x826b ;"Ｌ"
  .endarea
  ;6 key
  .org 0x0209218e
  .area 5*2
  .dh 0x826c ;"Ｍ"
  .dh 0x826d ;"Ｎ"
  .dh 0x826e ;"Ｏ"
  .endarea
  ;7 key
  .org 0x020921b6
  .area 5*2
  .dh 0x826f ;"Ｐ"
  .dh 0x8270 ;"Ｑ"
  .dh 0x8271 ;"Ｒ"
  .dh 0x8272 ;"Ｓ"
  .endarea
  ;8 key
  .org 0x020921d8
  .area 6*2
  .dh 0x8273 ;"Ｔ"
  .dh 0x8274 ;"Ｕ"
  .dh 0x8275 ;"Ｖ"
  .endarea
  ;9 key
  .org 0x02092166
  .area 5*2
  .dh 0x8276 ;"Ｗ"
  .dh 0x8277 ;"Ｘ"
  .dh 0x8278 ;"Ｙ"
  .dh 0x8279 ;"Ｚ"
  .endarea
  ;0 key
  .org 0x020921a2
  .area 5*2
  .dh 0x8140 ;"　"
  .endarea
.close
