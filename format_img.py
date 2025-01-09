import os
import struct
from hacktools import common, nitro


def readIMG(file):
    img = nitro.NCGR()
    img.tiles = []
    mapfile = None
    width = 256
    height = 256
    filesize = os.path.getsize(file)
    with common.Stream(file, "rb") as f:
        # Read header
        img.tileoff = f.readUInt()
        img.mapoff = f.readUInt()
        img.paloff = f.readUInt()
        img.unk1 = f.readUShort()
        img.unk2 = f.readUShort()
        img.unk3 = f.readUShort()
        img.unk4 = f.readUShort()
        img.unk5 = f.readByte()
        img.unk6 = f.readByte()
        img.unk7 = f.readUShort()
        img.unk8 = f.readUShort()
        img.bpp = img.unk6
        if img.bpp == 0x8 and img.unk7 > 0 and img.unk8 > 0:
            img.lineal = True
            width = img.unk7
            height = img.unk8
        common.logDebug(vars(img))
        # Read palettes
        f.seek(img.paloff)
        palsize = filesize - img.paloff
        palettes = []
        pallen = 0x200
        if palsize < pallen:
            pallen = palsize
        colornum = pallen // 2
        for i in range(palsize // pallen):
            palette = []
            for j in range(colornum):
                palette.append(common.readPalette(f.readUShort()))
            palettes.append(palette)
        indexedpalettes = {i: palettes[i] for i in range(0, len(palettes))}
        # Read tiles
        if img.unk4 == 1 and not img.lineal:
            # Start with a completely transparent tile
            tile = []
            for i2 in range(img.tilesize):
                for j2 in range(img.tilesize):
                    tile.append(0)
            img.tiles.append(tile)
        f.seek(img.tileoff)
        tiledata = f.read((img.mapoff if img.mapoff > 0 else img.paloff) - img.tileoff)
        tilelen = len(tiledata)
        for i in range(tilelen // (8 * img.bpp)):
            singletile = []
            for j in range(img.tilesize * img.tilesize):
                x = i * (img.tilesize * img.tilesize) + j
                if img.bpp == 4:
                    index = (tiledata[x // 2] >> ((x % 2) << 2)) & 0x0f
                else:
                    index = tiledata[x]
                singletile.append(index)
            img.tiles.append(singletile)
        # Read map
        if img.mapoff > 0:
            mapfile = nitro.NSCR()
            # Not sure why this is needed
            f.seek(img.mapoff)
            width = f.readUInt() * 8
            height = f.readUInt() * 8
            unk1 = f.readUInt()
            unk2 = f.readUInt()
            mapdata = f.read(img.paloff - img.mapoff - 0x10)
            for i in range(0, len(mapdata), 2):
                data = struct.unpack("<h", mapdata[i:i+2])[0]
                map = nitro.readMapData(data)
                if img.bpp == 0x4:
                    map.pal = 0
                mapfile.maps.append(map)
    common.logDebug("Loaded", len(img.tiles), "tiles")
    return img, mapfile, indexedpalettes, width, height


def readUncompressedIMG(file, palfile):
    img = nitro.NCGR()
    img.tiles = []
    width = 256
    if "cfont_0" in file:
        width = 16
    elif "cfont_1" in file:
        width = 8
    height = 256
    filesize = os.path.getsize(palfile)
    with common.Stream(palfile, "rb") as f:
        # Read palette
        palsize = filesize
        palettes = []
        pallen = 0x200
        if palsize < pallen:
            pallen = palsize
        colornum = pallen // 2
        if colornum > 16:
            img.bpp = 8
        for i in range(palsize // pallen):
            palette = []
            for j in range(colornum):
                palette.append(common.readPalette(f.readUShort()))
            palettes.append(palette)
        indexedpalettes = {i: palettes[i] for i in range(0, len(palettes))}
    filesize = os.path.getsize(file)
    with common.Stream(file, "rb") as f:
        # Read tiles
        tiledata = f.read()
        tilelen = len(tiledata)
        numpix = tilelen * 8 / img.bpp
        height = int(numpix // width)
        for i in range(tilelen // (8 * img.bpp)):
            singletile = []
            for j in range(img.tilesize * img.tilesize):
                x = i * (img.tilesize * img.tilesize) + j
                if img.bpp == 4:
                    index = (tiledata[x // 2] >> ((x % 2) << 2)) & 0x0f
                else:
                    index = tiledata[x]
                singletile.append(index)
            img.tiles.append(singletile)
    return img, None, indexedpalettes, width, height


def readImage(infolder, file, extension):
    palfile = file.replace(".bin", ".plb")
    if "_LZ" not in file and os.path.isfile(infolder + palfile):
        image, mapfile, palettes, width, height = readUncompressedIMG(infolder + file, infolder + palfile)
    else:
        image, mapfile, palettes, width, height = readIMG(infolder + file)
    return palettes, image, mapfile, None, width, height, "", ""


def extract(data):
    nitro.extractIMG(data + "extract_LZ/data/bg/", data + "out_IMG/", [".bin"], readImage)
