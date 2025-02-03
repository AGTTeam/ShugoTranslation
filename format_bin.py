import codecs
from hacktools import common, nds

binrange = [(0, 0)]
freeranges = [(0x938c0+0x300, 0x938c0+0x1000, True)]

def repack(data):
    binin = data + "extract/arm9.bin"
    binout = data + "repack/arm9.bin"
    headerin = data + "extract/header.bin"
    headerout = data + "repack/header.bin"

    with codecs.open(data + "fontconfig.txt", "r", "utf-8") as f:
        section = common.getSection(f, "", inorder=True)
        with common.Stream(data + "fontdata.bin", "wb") as f:
            for c in section:
                charid = c["name"].replace("～", "〜").encode("shift-jis")
                charlen = int(c["value"])
                f.write(charid)
                f.writeUShort(charlen)
            f.writeUShort(0)
            f.writeUShort(0xe)

    # Expand and repack the binary file
    nds.expandBIN(binin, binout, headerin, headerout, 0x2000, 0x021d1000)
    common.armipsPatch(common.bundledFile("bin_patch.asm"))


def extract(data):
    binin = data + "extract/arm9.bin"
    outfile = data + "bin_output.txt"

    nds.extractBIN((0x0, 0x938d8), binin=binin, binfile=outfile)
