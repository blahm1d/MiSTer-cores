# blahm1d MiSTer cores

**[Download downloader_blahm1d.ini](https://raw.githubusercontent.com/blahm1d/MiSTer-cores/main/downloader_blahm1d.ini)**

1. Place `downloader_blahm1d.ini` in your MiSTer's SD card root (`/media/fat/`).
2. Run **Update_All**.
3. Find the games under **Arcade → blahm1d**.

Run Update_All again whenever you want the latest published cores and updates.
Keep Update_All's Arcade ROMs option enabled for ROM downloads. This feed supplies
RBF cores and MRA definitions; it contains no game ROMs.

The INI uses MiSTer Downloader's [drop-in database support](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/main/docs/drop-in-databases.md).
Use a current Update_All installation. If your older installation does not pick
up drop-in files, update it or add the INI's two lines to your existing
`downloader.ini` once.

| Family | Included build |
| --- | --- |
| Gladiator | July 29 release; US and Japan |
| The Legend of Kage | August 30 water-priority fix; bootleg set 1 |
| Wolf Unit | August 3 master; seven original games |
| Y Unit | r36 family and r41 ADPCM/T2 lightgun builds; nine games |
| X Unit | September 14 clean Revolution X performance/audio build |
| T Unit | S12 ADPCM and DCS baselines; five games |
| Exidy 440 | r6 family; eleven games |
| NARC | v22 erase-row candidate |

**These releases include beta cores.** Read [release status and known issues](RELEASES.md)
before reporting a game issue. Most of the newer binaries still need cabinet
verification; a passing build does not establish that every game works correctly.

Each core has a distinct `blahm1d_` filename. This feed can coexist with other
MiSTer databases. MRAs keep their game profiles, ROM layouts and save filenames.
No global MiSTer settings are installed.

Generic Total Carnage and Revolution X NVRAM defaults are installed only if the
matching save file is absent. Downloader preserves an existing save. Use the
game/core's manual Save NVRAM action after changing settings or gun calibration.
Revolution X guns may need calibration for your display.

Source archives and original license notices are in [sources](sources/).
The exact RBF/MRA hashes and game list are in [catalog/releases.json](catalog/releases.json).

To publish future updates, follow [MAINTAINING.md](MAINTAINING.md). Pushing a
validated update to `main` automatically refreshes the downloader database.
