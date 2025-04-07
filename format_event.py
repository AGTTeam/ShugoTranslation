import codecs
import os
from hacktools import common

wordwrap = 307

def readString(f):
    addend = False
    sjis = common.detectEncodedString(f, startascii=[0x23, 0x24, 0x25])
    if sjis.endswith("$d"):
        sjis = sjis[:-2]
        addend = True
    sjis = sjis.replace("$n", "|")
    return sjis, addend


def repack(data):
    binin = data + "extract/data/msg/EventMsg.bin"
    binout = data + "repack/data/msg/EventMsg.bin"
    tfile = data + "event_input.txt"

    common.logMessage("Repacking EVENT from", tfile, "...")
    glyphs = {}
    with codecs.open(data + "fontconfig.txt", "r", "utf-8") as f:
        section = common.getSection(f, "", inorder=True)
        ascii = 0x20
        for c in section:
            charid = c["name"].replace("～", "〜").encode("shift-jis")
            charlen = int(c["value"])
            glyphs[chr(ascii)] = common.FontGlyph(0, charlen, charlen + 2)
            glyphs[charid] = common.FontGlyph(0, charlen, charlen + 2)
            ascii += 1

    filesize = os.path.getsize(binin)
    i = 0
    chartot = transtot = 0
    common.copyFile(binin, binout)
    with codecs.open(tfile, "r", "utf-8") as f:
        section = common.getSection(f, "", comment="##")
        chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
    with common.Stream(binout, "rb+") as fin:
            while i * 0x90 < filesize:
                fin.seek(i * 0x90)
                addend = False
                sjis, addend = readString(fin)
                if sjis == "ｔｅｓｔ":
                    i += 1
                    continue
                newsjis = ""
                if sjis in section:
                    newsjis = section[sjis].pop(0)
                    if len(section[sjis]) == 0:
                        del section[sjis]
                if newsjis == "!":
                    sjis = ""
                elif newsjis != "":
                    sjis = newsjis.replace("‘", "[").replace("’", "]").replace("“", "{").replace("”", "}").replace("♪", "%").replace("×", "@")
                    sjis = common.wordwrap(sjis, glyphs, wordwrap, detectTextCode)
                sjis = sjis.replace("|", "$n")
                if addend:
                    sjis += "$d"
                fin.seek(i * 0x90)
                fin.writeZero(0x90)
                fin.seek(i * 0x90)
                common.writeEncodedString(fin, sjis, 0x8f)
                i += 1
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))


def extract(data):
    binin = data + "extract/data/msg/EventMsg.bin"
    tfile = data + "event_output.txt"

    common.logMessage("Extracting EVENT to", tfile, "...")
    filesize = os.path.getsize(binin)
    i = 0
    with common.Stream(binin, "rb") as fin:
        with codecs.open(tfile, "w", "utf-8") as f:
            while i * 0x90 < filesize:
                fin.seek(i * 0x90)
                #pos = fin.tell()
                sjis, _ = readString(fin)
                i += 1
                if sjis == "ｔｅｓｔ":
                    continue
                #f.write(common.toHex(pos))
                f.write(sjis + "=\n")
    common.logMessage("Done! Extracted", i, "lines")


def detectTextCode(s, i=0):
    if s[i] == "#":
        return 2
    if s[i] == "$":
        if s[i+1] == "t" or s[i+1] == "s" or s[i+1] == "v":
            return 4
        if s[i+1] == "c":
            return 3
        return 2
    return 0
