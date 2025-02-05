import codecs
from hacktools import common, nds

binrange = [(0x930b8, 0x9327f)]
freeranges = [(0x938c0+0x300, 0x938c0+0x1000, True)]

def repack(data):
    binin = data + "extract/arm9.bin"
    binfile = data + "bin_input.txt"
    binout = data + "repack/arm9.bin"
    headerin = data + "extract/header.bin"
    headerout = data + "repack/header.bin"
    pswfile = data + "psw_input.txt"

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
    nds.repackBIN(binrange, freeranges, binin=binin, binout=binout, binfile=binfile, injectstart=0x021d1000-0x938c0, nocopy=True)
    # Repack passwords
    with codecs.open(pswfile, "r", "utf-8") as f:
        section = common.getSection(f, "", inorder=True)
    with common.Stream(binout, "rb+") as f:
        f.seek(0x8b93c)
        for c in section:
            newpsw = c["name"] if c["value"] == "" else c["value"]
            for i in range(10):
                if i >= len(newpsw):
                    f.writeUShort(0x8140)
                else:
                    encch = newpsw[i].encode("shift-jis")
                    if len(encch) != 2:
                        common.logError("Invalid password, can only contain shift-jis characters:", newpsw)
                        break
                    f.write(encch[::-1])
            if i < len(newpsw) - 1:
                common.logError("Password is too long:", newpsw)
    # Apply ASM patch
    common.armipsPatch(common.bundledFile("bin_patch.asm"))


def extract(data):
    binin = data + "extract/arm9.bin"
    outfile = data + "bin_output.txt"
    pswfile = data + "psw_output.txt"

    # Extract passwords
    with codecs.open(pswfile, "w", "utf-8") as out:
        with common.Stream(binin, "rb") as f:
            f.seek(0x8b93c)
            # There are 13 passwords with a fixed length of 10, padded with spaces on the right
            for _ in range(13):
                psw = ""
                for __ in range(10):
                    psw += f.read(2)[::-1].decode("shift-jis")
                out.write(psw.rstrip("　") + "=\n")

    nds.extractBIN(binrange, binin=binin, binfile=outfile, writepos=True)
