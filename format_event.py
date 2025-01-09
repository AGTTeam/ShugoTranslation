import codecs
import os
from hacktools import common


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
                pos = fin.tell()
                s = common.detectEncodedString(fin, startascii=[0x23, 0x24, 0x25])
                if s.endswith("$d"):
                    s = s[:-2]
                s = s.replace("$n", "|")
                i += 1
                if s == "ｔｅｓｔ":
                    continue
                #f.write(common.toHex(pos))
                f.write(s + "=\n")
    common.logMessage("Done! Extracted", i, "lines")
