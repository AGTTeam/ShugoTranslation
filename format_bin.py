from hacktools import common, nds, nitro


def extract(data):
    binin = data + "extract/arm9.bin"
    outfile = data + "bin_output.txt"

    nds.extractBIN((0x0, 0x938d8), binin=binin, binfile=outfile)
