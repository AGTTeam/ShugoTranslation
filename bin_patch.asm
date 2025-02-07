.nds

.open "ShugoData/repack/arm9.bin",0x021d1000 - 0x938c0 ;fix first value is wrong
  .orga 0x938c0
  .area 0x500

  ;ASCII to SJIS lookup table, also includes VWF values
  SJIS_LOOKUP:
  .import "ShugoData/fontdata.bin"
  .align

  IS_ASCII:
  .dw 0
  VWF_LEN:
  .dw 0

  IS_ASCII_BIN:
  .dw 0
  VWF_LEN_BIN:
  .dw 0
  APPLY_BIN:
  .dw 0

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

  ;Again the same as above but convert r2/r1 and store the value in a separate addr
  LOAD_ASCII_BIN:
  push {r3-r5}
  ldr r3,=APPLY_BIN
  ldr r3,[r3]
  cmp r3,0x0
  beq @@ret
  and r5,r2,0xff
  cmp r5,0x7f
  bgt @@sjis
  ldr r3,=SJIS_LOOKUP
  sub r4,r5,0x20
  lsl r4,r4,0x2
  add r3,r3,r4
  ldrb r2,[r3]
  ldrb r1,[r3,0x1]
  ldrb r4,[r3,0x2]
  ;Save the VWF value and set IS_ASCII_BIN to 1
  ldr r3,=IS_ASCII_BIN
  str r4,[r3,0x4]
  mov r4,1
  str r4,[r3]
  b @@ret
  @@sjis:
  ;Set IS_ASCII_BIN to 0, set vwf value to the fixed value and return
  ldr r3,=IS_ASCII_BIN
  mov r4,0
  str r4,[r3]
  mov r4,0xc
  str r4,[r3,0x4]
  @@ret:
  pop {r3-r5}
  mov r0,r2,lsl 0x10
  bx lr
  .pool

  ADVANCE_SCRIPT_BIN:
  push {r1-r2}
  ldr r1,=IS_ASCII_BIN
  ldr r2,[r1]
  cmp r2,1
  addne r0,r0,0x2
  addeq r0,r0,0x1
  mov r2,0
  str r2,[r1]
  pop {r1-r2}
  bx lr
  .pool

  VWF_BIN:
  push {r2}
  ldr r2,=APPLY_BIN
  ldr r2,[r2]
  cmp r2,0x0
  addeq r0,r1,r0
  beq @@ret
  ldr r2,=VWF_LEN_BIN
  ldr r2,[r2]
  add r0,r1,r2
  @@ret:
  pop {r2}
  bx lr
  .pool

  ;Wrap this function call so we only apply VWF when it's called from a specific function
  ;We don't need it in other places like the password menu
  WRAP_PRINT_BIN_STR:
  push {lr}
  push {r0-r1}
  ldr r0,=APPLY_BIN
  mov r1,0x1
  str r1,[r0]
  pop {r0-r1}
  bl 0x020693f4
  push {r0-r1}
  ldr r0,=APPLY_BIN
  mov r1,0x0
  str r1,[r0]
  pop {r0-r1}
  pop {lr}
  bx lr
  .pool

  LOAD_DAKUTEN_LIST:
  cmp r5,0x9
  ldrne r2,[r2,r5,lsl 0x2]
  bne @@ret
  ldr r2,=DAKUTEN_LIST
  @@ret:
  bx lr
  .pool
  
  LOAD_DAKUTEN_NUM:
  cmp r5,0x9
  moveq r1,0x3
  beq @@ret
  ldrb r1,[r0,r5]
  @@ret:
  bx lr
  .endarea
.close

.open "ShugoData/repack/arm9.bin",0x02000000
  ;Event ASCII/VWF

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

  ;Decrease line height
  .org 0x020356bc
  ;add r0,r0,0x17
  add r0,r0,0x10
  ;Move everything up
  .org 0x0203ad9c
  ;mov r2,0x98
  mov r2,0x90


  ;BIN ASCII/VWF

  ;Don't skip ASCII characters
  .org 0x02069424
  ;bcc 0x02069600
  nop

  ;Jump here to convert character to SJIS
  .org 0x02069444
  ;mov r0,r2,lsl 0x10
  bl LOAD_ASCII_BIN

  ;Always jump here, don't limit line length
  .org 0x020695c4
  ;bge 0x020695e0
  b 0x020695e0

  ;Extend the max len for these lines
  .org 0x02071c4c
  ;mov r1,0x19
  mov r1,0x30
  .org 0x02071c8c
  ;mov r1,0x19
  mov r1,0x30
  .org 0x02071ccc
  ;mov r1,0x19
  mov r1,0x30

  ;Apply VWF here
  .org 0x020695e8
  ;add r0,r1,r0
  bl VWF_BIN

  ;Only advance 1 byte if char was ASCII
  .org 0x020695f4
  ;add r0,r0,0x2
  bl ADVANCE_SCRIPT_BIN

  ;Wrap these calls so we know when to apply the VWF
  .org 0x0206939c
  ;bl 0x020693f4
  bl WRAP_PRINT_BIN_STR
  .org 0x020693d0
  ;bl 0x020693f4
  bl WRAP_PRINT_BIN_STR


  ;Password menu

  ;Change the behavior of the dakuten button to act as a normal one
  ;Jump to the other button execution instead of the dakuten code
  .org 0x02067e5c
  ;beq 0x02067e6c
  beq 0x02067fec

  ;Load the correct key list
  .org 0x02068044
  ;ldr r2,[r2,r5,lsl 0x2]
  bl LOAD_DAKUTEN_LIST
  .org 0x020680d8
  ;ldr r2,[r2,r5,lsl 0x2]
  bl LOAD_DAKUTEN_LIST

  ;Load the correct character num
  .org 0x020680bc
  ;ldrb r1,[r0,r5]
  bl LOAD_DAKUTEN_NUM

  ;The amount of characters for each phone key
  .org 0x0208b894
  .db 0x3 ;1
  .db 0x3 ;2
  .db 0x3 ;3
  .db 0x3 ;4
  .db 0x3 ;5
  .db 0x3 ;6
  .db 0x3 ;7
  .db 0x3 ;8
  .db 0x2 ;9
  .db 0x1 ;0

  ;Redefine the characters for each key
  ;no need to change the pointer since there's enough space
  ;1 key
  .org 0x020921e4
  .area 10*2
  .dh 0x8344 ;Ａ/ゥ
  .dh 0x8345 ;Ｂ/ウ
  .dh 0x8346 ;Ｃ/ェ
  .endarea
  ;2 key
  .org 0x0209217a
  .area 5*2
  .dh 0x8347 ;Ｄ/エ
  .dh 0x8348 ;Ｅ/ォ
  .dh 0x8349 ;Ｆ/オ
  .endarea
  ;3 key
  .org 0x02092198
  .area 5*2
  .dh 0x834a ;Ｇ/カ
  .dh 0x834b ;Ｈ/ガ
  .dh 0x834c ;Ｉ/キ
  .endarea
  ;4 key
  .org 0x020921cc
  .area 6*2
  .dh 0x834d ;Ｊ/ギ
  .dh 0x834e ;Ｋ/ク
  .dh 0x834f ;Ｌ/グ
  .endarea
  ;5 key
  .org 0x02092170
  .area 5*2
  .dh 0x8350 ;Ｍ/ケ
  .dh 0x8351 ;Ｎ/ゲ
  .dh 0x8352 ;Ｏ/コ
  .endarea
  ;6 key
  .org 0x0209218e
  .area 5*2
  .dh 0x8353 ;Ｐ/ゴ
  .dh 0x8354 ;Ｑ/サ
  .dh 0x8355 ;Ｒ/ザ
  .endarea
  ;7 key
  .org 0x020921b6
  .area 5*2
  .dh 0x8356 ;Ｓ/シ
  .dh 0x8357 ;Ｔ/ジ
  .dh 0x8358 ;Ｕ/ス
  .endarea
  ;8 key
  .org 0x020921d8
  .area 6*2
  .dh 0x8359 ;Ｖ/ズ
  .dh 0x835a ;Ｗ/セ
  .dh 0x835b ;Ｘ/ゼ
  .endarea
  ;9 key
  .org 0x02092166
  .area 5*2
  .dh 0x835c ;Ｙ/ソ
  .dh 0x835d ;Ｚ/ゾ
  .endarea
  ;0 key
  .org 0x020921a2
  .area 5*2
  .dh 0x8340 ;　/ァ
  DAKUTEN_LIST:
  .dh 0x8341 ;！/ア
  .dh 0x8342 ;？/ィ
  .dh 0x8343 ;＆/イ
  .endarea
.close
