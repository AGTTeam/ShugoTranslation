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
        img.tileoffset = f.readUInt()
        img.mapoffset = f.readUInt()
        img.paloffset = f.readUInt()
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
        f.seek(img.paloffset)
        palsize = filesize - img.paloffset
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
        f.seek(img.tileoffset)
        tilelen = (img.mapoffset if img.mapoffset > 0 else img.paloffset) - img.tileoffset
        tiledata = f.read(tilelen)
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
        if img.mapoffset > 0:
            mapfile = nitro.NSCR()
            # Not sure why this is needed
            f.seek(img.mapoffset)
            width = f.readUInt() * 8
            height = f.readUInt() * 8
            unk1 = f.readUInt()
            unk2 = f.readUInt()
            mapdata = f.read(img.paloffset - img.mapoffset - 0x10)
            for i in range(0, len(mapdata), 2):
                data = struct.unpack("<h", mapdata[i:i+2])[0]
                map = nitro.readMapData(data)
                if img.bpp == 0x4:
                    map.pal = 0
                mapfile.maps.append(map)
    common.logDebug("Loaded", len(img.tiles), "tiles")
    return img, mapfile, indexedpalettes, width, height


def readUncompressedIMG(file, palfile, objfile=False):
    img = nitro.NCGR()
    img.tiles = []
    filesize = os.path.getsize(palfile)
    with common.Stream(palfile, "rb") as f:
        # Read palette
        palsize = filesize
        palettes = []
        pallen = 0x200
        if palsize < pallen:
            pallen = palsize
        colornum = pallen // 2
        if colornum > 16 and not objfile:
            img.bpp = 8
        for i in range(palsize // pallen):
            palette = []
            for j in range(colornum):
                palette.append(common.readPalette(f.readUShort()))
            palettes.append(palette)
        indexedpalettes = {i: palettes[i] for i in range(0, len(palettes))}
    filesize = os.path.getsize(file)
    if not objfile:
        width = 256
        if "cfont_0" in file:
            width = 16
        elif "cfont_1" in file:
            width = 8
        height = 256
    else:
        width = 256
        numpix = filesize * 8 / img.bpp
        height = (filesize // (width // 8)) * 8
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


def writeImage(workfolder, infolder, outfolder, file, image, palettes, map, cell, width, height):
    palfile = file.replace(".bin", ".plb")
    if "_LZ" not in file and os.path.isfile(infolder + palfile):
        return image, palettes, map, cell, width, height, False
    if "pbg005" not in file:
        return None, None, None, None, 0, 0, False
    pngfile = file.replace(".bin", ".png")
    nitro.writeNSCR(outfolder + file, image, map, workfolder + pngfile, palettes, width, height)
    return None, None, None, None, 0, 0, False


def readImage(infolder, file, extension):
    palfile = file.replace(".bin", ".plb")
    if "_LZ" not in file and os.path.isfile(infolder + palfile):
        image, mapfile, palettes, width, height = readUncompressedIMG(infolder + file, infolder + palfile)
    else:
        image, mapfile, palettes, width, height = readIMG(infolder + file)
    return palettes, image, mapfile, None, width, height, "", ""


def readOBJImage(infolder, file, extension):
    palfile = ""
    if "_ch" in file and "/lib_" not in file and "/tb_" not in file:
        palfile = file.replace("_ch", "_pa")
    elif "objchar" in file:
        palfile = file.replace("objchar", "objplt")
    if "Btl_Enemy_ch018.bin" in file:
        palfile = ""
    if palfile == "":
        return None, None, None, None, 0, 0, "", ""
    palfile = palfile.replace("menu_item_pa001.bin", "menu_item_pa000.bin")
    palfile = palfile.replace("menu_item_pa003.bin", "menu_item_pa002.bin")
    palfile = palfile.replace("Btl_Target_pa005.bin", "Btl_Target_pa004.bin")
    palfile = palfile.replace("menu_info_pa003.bin", "menu_info_pa002.bin")
    palfile = palfile.replace("menu_item_pa.bin", "menu_item_pa000.bin")
    palfile = palfile.replace("menu_item_pa001.bin", "menu_item_pa000.bin")
    palfile = palfile.replace("com_num32_pa", "com_num_pa")
    palfile = palfile.replace("com_num_pa004.bin", "com_num_pa003.bin")
    palfile = palfile.replace("com_num_pa006.bin", "com_num_pa005.bin")
    palfile = palfile.replace("story_item_pa001.bin", "story_item_pa000.bin")
    palfile = palfile.replace("story_item_pa002.bin", "story_item_pa000.bin")
    image, mapfile, palettes, width, height = readUncompressedIMG(infolder + file, infolder + palfile, True)
    return palettes, image, mapfile, None, width, height, "", ""


def repack(data):
    nitro.repackIMG(data + "work_IMG/", data + "extract_LZ/data/bg/", data + "repack_LZ/data/bg/", [".bin"], readImage, writeImage, clean=True)


def extract(data):
    nitro.extractIMG(data + "extract_LZ/data/bg/", data + "out_IMG/", [".bin"], readImage)
    # This would need reverse-engineering the style_*.bin files containing the cell data
    # nitro.extractIMG(data + "extract_LZ/data/obj/", data + "out_OBJ/", [".bin"], readOBJImage)
