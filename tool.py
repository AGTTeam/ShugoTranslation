import click
import os
from hacktools import common, nds, nitro

version = "0.2.0"
data = "ShugoData/"
romfile = "shugo.nds"
rompatch = data + "shugo_patched.nds"
infolder = data + "extract/"
infolderlz = data + "extract_LZ/"
repacklz = data + "repack_LZ/"
replacefolder = data + "replace/"
replacelz = data + "replace_LZ/"
outfolder = data + "repack/"
bannerfile = data + "repack/banner.bin"
patchfile = data + "patch.xdelta"


@common.cli.command()
@click.option("--rom", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--n3d", is_flag=True, default=False)
@click.option("--event", is_flag=True, default=False)
def extract(rom, bin, img, n3d, event):
    all = not rom and not bin and not img and not n3d and not event
    if all or rom:
        nds.extractRom(romfile, infolder, outfolder)
        common.logMessage("Decompressing files ...")
        common.makeFolder(infolderlz)
        for file in common.showProgress(common.getFiles(infolder, [".bin", ".lz", ".plb"])):
            common.makeFolders(infolderlz + os.path.dirname(file))
            if file.endswith("_LZ.bin") or file.endswith(".lz"):
                nds.decompressFile(infolder + file, infolderlz + file)
            else:
                common.copyFile(infolder + file, infolderlz + file)
        common.makeFolder(repacklz)
        common.logMessage("Done!")
    if all or bin:
        import format_bin
        format_bin.extract(data)
    if all or img:
        import format_img
        format_img.extract(data)
    if all or n3d:
        common.logMessage("Extracting N3D ...")
        n3din = infolderlz + "data/n3d/"
        n3dout = data + "out_N3D/"
        common.makeFolder(n3dout)
        for file in common.showProgress(common.getFiles(n3din, [".bin"])):
            if file.endswith("tx_LZ.bin"):
                nsbmd = nitro.readNSBTX(n3din + file)
                if nsbmd is not None and len(nsbmd.textures) > 0:
                    common.makeFolders(n3dout + os.path.dirname(file))
                    for texi in range(len(nsbmd.textures)):
                        nitro.drawNSBMD(n3dout + file.replace(".bin", "") + "_" + nsbmd.textures[texi].name + ".png", nsbmd, texi)
        common.logMessage("Done!")
    if all or event:
        import format_event
        format_event.extract(data)


@common.cli.command()
@click.option("--no-rom", is_flag=True, default=False, hidden=True)
@click.option("--img", is_flag=True, default=False)
@click.option("--event", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
def repack(no_rom, img, event, bin):
    all = not img and not event and not bin
    if all or img:
        import format_img
        format_img.repack(data)
    if all or event:
        import format_event
        format_event.repack(data)
    if all or bin:
        import format_bin
        format_bin.repack(data)
    if not no_rom:
        if os.path.isdir(replacelz):
            common.mergeFolder(replacelz, repacklz)
        common.logMessage("Compressing files ...")
        for file in common.showProgress(common.getFiles(repacklz, [".bin", ".lz", ".plb"])):
            if file.endswith("_LZ.bin") or file.endswith(".lz"):
                nds.compressFile(repacklz + file, outfolder + file, nds.CompressionType.LZ10)
            else:
                common.copyFile(repacklz + file, outfolder + file)
        common.logMessage("Done!")
        if os.path.isdir(replacefolder):
            common.mergeFolder(replacefolder, outfolder)
        nds.editBannerTitle(bannerfile, "Shugo Chara!\nNorinori! Chara-narhythm\nKonami Digital Entertainment")
        nds.repackRom(romfile, rompatch, outfolder, patchfile)


if __name__ == "__main__":
    common.setupTool("ShugoTranslation", version, data, romfile, 0xaab4207f)
