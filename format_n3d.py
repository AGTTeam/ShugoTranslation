
import math
import os
from hacktools import common, nitro


def repack(data):
    common.logMessage("Repacking N3D ...")
    n3din = data + "extract_LZ/data/n3d/"
    n3dout = data + "repack_LZ/data/n3d/"
    n3dwork = data + "work_N3D/"
    for file in common.showProgress(common.getFiles(n3din, [".bin"])):
        if file.endswith("tx_LZ.bin"):
            copied = False
            nsbmd = nitro.readNSBTX(n3din + file)
            if nsbmd is not None and len(nsbmd.textures) > 0:
                for texi in range(len(nsbmd.textures)):
                    pngfile = n3dwork + file.replace(".bin", "") + "_" + nsbmd.textures[texi].name + ".png"
                    if not os.path.isfile(pngfile):
                        continue
                    if not copied:
                        common.makeFolders(n3dout + os.path.dirname(file))
                        common.copyFile(n3din + file, n3dout + file)
                        copied = True
                    nitro.writeNSBMD(n3dout + file, nsbmd, texi, pngfile)
        else:
            pngfile = n3dwork + file.replace(".bin", ".png")
            if not os.path.isfile(pngfile):
                continue
            common.makeFolders(n3dout + os.path.dirname(file))
            common.copyFile(n3din + file, n3dout + file)
            # Check if file is STEX
            with common.Stream(n3din + file, "rb") as f:
                if f.readString(4) == "STEX":
                    common.logDebug("Reading STEX file", file)
                    stex = readSTEX(f)
                    if stex is not None:
                        nitro.writeNSBMD(n3dout + file, stex, 0, pngfile)
    common.logMessage("Done!")


def extract(data):
    common.logMessage("Extracting N3D ...")
    n3din = data + "extract_LZ/data/n3d/"
    n3dout = data + "out_N3D/"
    common.makeFolder(n3dout)
    for file in common.showProgress(common.getFiles(n3din, [".bin"])):
        if file.endswith("tx_LZ.bin"):
            nsbmd = nitro.readNSBTX(n3din + file)
            if nsbmd is not None and len(nsbmd.textures) > 0:
                common.makeFolders(n3dout + os.path.dirname(file))
                for texi in range(len(nsbmd.textures)):
                    nitro.drawNSBMD(n3dout + file.replace(".bin", "") + "_" + nsbmd.textures[texi].name + ".png", nsbmd, texi)
        else:
            # Check if file is STEX
            with common.Stream(n3din + file, "rb") as f:
                if f.readString(4) == "STEX":
                    common.logDebug("Reading STEX file", file)
                    stex = readSTEX(f)
                    if stex is not None:
                        nitro.drawNSBMD(n3dout + file.replace(".bin", ".png"), stex, 0)
    common.logMessage("Done!")


def readSTEX(f):
    stex = nitro.NSBMD()
    tex = nitro.NSBMDTexture()
    pal = nitro.NSBMDPalette()
    tex.offset = 0x20
    tex.size = f.readUInt()
    # Some files are just palettes, skip them
    if tex.size == 0:
        return None
    pal.size = f.readUInt()
    tex.width = f.readUShort()
    tex.height = f.readUShort()
    tex.format = f.readByte()
    tex.unk1 = f.readByte()
    tex.unk2 = f.readByte()
    tex.const1 = f.readByte()  # always 1?
    common.logDebug(common.varsHex(tex))
    # Round up size to the next power of 2
    widthp = int(math.log2(tex.width))
    if 2 ** widthp != tex.width:
        tex.width = 2 ** (widthp + 1)
    heightp = int(math.log2(tex.height))
    if 2 ** heightp != tex.height:
        tex.height = 2 ** (heightp + 1)
    # Read texture data
    f.seek(tex.offset)
    tex.data = f.read(tex.size)
    stex.textures.append(tex)
    # Read palette
    pal.offset = tex.offset + tex.size
    f.seek(pal.offset)
    for i in range(pal.size // 2):
        pal.data.append(common.readPalette(f.readUShort()))
    stex.palettes.append(pal)
    return stex
