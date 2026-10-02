# blahm1d MiSTer cores

**[Download downloader_blahm1d.ini](https://mister.blahm1d.com/downloader_blahm1d.ini)** (right-click the link and choose *Save link as*)

[ZIP download](https://mister.blahm1d.com/downloader_blahm1d.zip) (extract the INI first).

1. Place `downloader_blahm1d.ini` in your MiSTer's SD card root (`/media/fat/`).
2. Run **Update_All**.
3. Find the games under **Arcade > Blahm1d** (regional versions under **alternatives** inside Blahm1d).

Run Update_All again whenever you want the latest published cores and updates.
This feed supplies RBF cores and MRA game definitions.
**No ROMs are included.** Enable ROM downloads in Update_All, or **BYOR** (bring your own ROMs).
ROM compatibility has been tested with a MAME 0.289 merged set.
War Gods also requires your own disk image.

The INI uses MiSTer Downloader's [drop-in database support](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/main/docs/drop-in-databases.md).
Use a current Update_All installation. If your older installation does not pick
up drop-in files, update it or add the INI's two lines to your existing
`downloader.ini` once.

| Family | Included build |
| --- | --- |
| Mortal Kombat 4 (Zeus 1) | September 30 v9 fighter lighting and Lighting Toggle; cabinet verified; all 132 timing checks passed |
| Gladiator | July 29 release; US and Japan |
| The Legend of Kage | August 30 water-priority fix; bootleg set 1 |
| Wolf Unit | September 28 power-cycle save fix, flip fence and DCS sound fix; seven original games |
| Y Unit | RC3 sound and CMOS fixes (family and ADPCM/T2 lightgun builds); nine games |
| X Unit | September 18 Revolution X mouse + sprite-cache build |
| T Unit | September 22 announcer fix (ADPCM); September 23 DCS sound fix (Mortal Kombat II); five games |
| Exidy 440 | r6 family; eleven games |
| NARC | September 28 v24 saves and HUD-row fix |
| Night Slashers | July 12 v1.4 sprite-fade fix; Japan, Korea and Over Sea |
| V Unit | Cruis'n USA, Cruis'n World and Off Road Challenge (one core, r30) and War Gods (r16; bring your own disk image) |

**These releases include beta cores.** Read [release status and known issues](RELEASES.md)
before reporting a game issue. Cabinet confirmation for the T Unit DCS build is
not yet recorded; a passing build does not establish that every game works correctly.

Each core has a distinct `blahm1d_` filename. This feed can coexist with other
MiSTer databases. MRAs keep their game profiles, ROM layouts and save filenames.
Game entries keep their ` [blahm1d]` filenames inside the Blahm1d folder; this
folder change does not rename saves or DIP settings.
No global MiSTer settings are installed.

Generic Total Carnage and Revolution X NVRAM defaults are installed only if the
matching save file is absent. Downloader preserves an existing save. Use the
game/core's manual Save NVRAM action after changing settings or gun calibration.
Revolution X guns may need calibration for your display.

Source archives and original license notices are in [sources](sources/).
The exact RBF/MRA hashes and game list are in [catalog/releases.json](catalog/releases.json).

To publish future updates, follow [MAINTAINING.md](MAINTAINING.md). Pushing a
validated update to `main` automatically refreshes the downloader database.
