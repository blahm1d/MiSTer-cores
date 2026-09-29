# Release status - 2026-09-29

13 RBFs and 44 MRAs. September 22-29 updates: Wolf Unit (save fix), NARC (v24 saves), T Unit (ADPCM and DCS), Y Unit (both builds), and the V Unit collection (Cruis'n USA, Cruis'n World, Off Road Challenge, War Gods r16).

## Gladiator - 2026-07-29 release

Existing public release. Gladiator (US) and Ougon no Shiro (Japan). The newer OSD contract source draft has no new binary.

RBF: `blahm1d_gladiator_20260729.rbf`

SHA-256: `1857e3ca16709c2031a67b0bac6e6d0d1f89f23a37f71d082ee3271807ee5d04`

Games: Gladiator (US) [DIP CRT Guard 20260729]; Ougon no Shiro (Japan).

## The Legend of Kage - Water priority r2

Beta; four-corner timing passed. Bootleg set 1. Water/sprite priority fix; cabinet verification pending. The later CRT geometry source draft is not in this binary.

RBF: `blahm1d_legendofkage_20260830.rbf`

SHA-256: `896a574d681f16d59e38fb2a163a40d7b3b1d3648e0af35ef64a17a6dc4ccb4e`

Games: The Legend of Kage (bootleg set 1).

## Wolf Unit - Save fix (power cycle)

Beta; cabinet verified; timing passed at all corners. Seven original Wolf Unit games. Settings and high scores now survive a power cycle (they were restored corrupted on every power-on; a reset kept them). MK3 and UMK3 always start at the default volume after a power cycle, as the original games do; the other five keep it. Includes the page-flip fix for MK3/UMK3 Motaro/Kintaro/Shiva HUD and sprite flashing, and the DCS 16x output filter (hiss fix). Community hacks requiring separate ROM sources are not installed by this feed.

RBF: `blahm1d_wolfunit_20260928.rbf`

SHA-256: `30105f477f0f35a6fa080cda148994099c6b4be2fe8cdbee6481df9c071552dc`

Games: Mortal Kombat 3 (rev 2.1); NBA Hangtime (L1.3 10/10/96); NBA Maximum Hangtime (L1.03 06/09/97); NHL Open Ice: 2 on 2 Challenge (rev 1.21); Rampage: World Tour (rev 1.3); Ultimate Mortal Kombat 3 (rev 1.2); WWF: WrestleMania (rev 1.30 08/10/95).

## Y Unit - Family RC3

Beta; cabinet verified; timing waiver (misses only the slow -40C corner by 0.018 ns). Smash TV, Trog, High Impact, Super High Impact, Strike Force and Saurian Front. Fixes silent sound at power-on (6809 sound CPU cold reset) and the CMOS INVALID hang on a blank save (factory CMOS built into the MRAs); blitter bit-exact against MAME.

RBF: `blahm1d_yunit_20260922.rbf`

SHA-256: `7a1f6d03ae6f7a7dcb11bf8882ef065f72bab5e077eae830a5f4ba653d232213`

Games: High Impact Football (rev LA5 02/15/91); Saurian Front (proto v5.0 08/07/90); Smash T.V. (rev 8.00); Strike Force (rev 1 02/25/91); Super High Impact (rev LA2 10/22/91); Trog (rev LA5 3/29/91).

## Y Unit - ADPCM / T2 guns RC3

Beta; cabinet verified; timing passed at all corners. Mortal Kombat Y Unit, Terminator 2 and Total Carnage. Fixes silent sound at power-on, crackly sampled speech (OKI ADPCM now matches MAME) and the CMOS INVALID hang on a blank save. Per-player guns, Sinden border and crosshair controls.

RBF: `blahm1d_yunitadpcm_20260922.rbf`

SHA-256: `1487bdb1a7f5a9b1d55920d746921c87faa0d1db5ecf7a26db505d888bc5b7d6`

Games: Mortal Kombat (rev 4.0 09/28/92, Y-Unit); Terminator 2 - Judgment Day (rev LA4 08/03/92); Total Carnage (rev LA1 03/10/92).

## X Unit - Revolution X mouse + sprite cache

Beta; cabinet verified; slow-corner setup waiver (-0.195/-0.171 ns), fast corners and hold pass. Revolution X. OSD Gun = Mouse now works (left Trigger, right Action). 128 KB sprite cache for the post-helicopter pan-down slowdown. Keeps Music/SFX volume controls.

RBF: `blahm1d_xunit_20260918.rbf`

SHA-256: `8bd67839b1070c556eaaa331253daddc4c5c34d1753d70439ccbcceb2337d15c`

Games: Revolution X.

## Exidy cores - Exidy 440 r6

Beta; cabinet verified; four-corner timing passed. Eleven Exidy 440 games.

RBF: `blahm1d_exidy440_20260907.rbf`

SHA-256: `b56e3467b5863e48cd89a8256a3ab134f3df60c6f94b201f0663ae988da5e116`

Games: Catch-22; Cheyenne; Chiller; Clay Pigeon; Combat; Crackshot; Crossbow; Hit 'n Miss; Showdown; Top Secret; Who Dunit.

## NARC - v24 saves

Beta; cabinet verified; timing passed at all corners. NARC rev 7.00. Now keeps high scores, operator adjustments (difficulty, lives, coinage, free play) and bookkeeping across power cycles; save with the OSD's Save NVRAM. Keeps the v23 fix for the garbage row at the bottom of the top HUD. NARC has no software volume (the original uses a hardware pot).

RBF: `blahm1d_narc_20260928.rbf`

SHA-256: `bf2c532935152064ca8244397a3b4910c8cad089efecb14012aead2ff99fea64`

Games: Narc (rev 7.00).

## T Unit - ADPCM R7E announcer fix

Beta; cabinet verified; timing passed at all corners. OKI ADPCM sound now matches MAME, fixing the NBA Jam announcer crackle. NBA/TE scaling repair retained. Popup flashing, cold-boot sound and save persistence issues from the S12 baseline may remain.

RBF: `blahm1d_tunit_20260922.rbf`

SHA-256: `a7724b6be160853a4edc2762faf37c9877465c13bbcee26b50bc8cb1e6ff4c9c`

Games: Judge Dredd (rev TA1 7/12/92, location test); Mortal Kombat (rev 5.0 T-Unit 03/19/93); NBA Jam (rev 3.01 4/07/93); NBA Jam Tournament Edition (rev 4.0 3/23/94).

## T Unit - DCS sound fix

Beta; timing passed at all corners. Mortal Kombat II. DCS audio 16x polyphase output filter (hiss fix). Cabinet confirmation not yet recorded; save behavior remains under development.

RBF: `blahm1d_tunitdcs_20260923.rbf`

SHA-256: `f7c8861da1a6105809e73cc77de452fea8bc5273989f429519eb2eb19b8c7574`

Games: Mortal Kombat II (rev L3.1).

## Selection notes

T Unit ADPCM moved from the S12 baseline to the September 22 R7E announcer-fix build; the S20/S22 builds rejected on the cabinet stay excluded. T Unit DCS moved to the September 23 sound-fix build. These builds still have documented limitations.

## V Unit - Cruis'n family r30

Beta; cabinet verified; timing passed at all corners. One core for Cruis'n USA, Cruis'n World and Off Road Challenge, the whole game in the FPGA at arcade speed. Full analog steering in Cruis'n World (map Test, then run Calibrate Controls once). New mappable Test, Service, Volume Up/Down and Nitro (Off Road) buttons, appended so saved button maps stay valid. OSD options for analog pedals on the right stick, pots on the DE10-Nano ADC header, and cabinet switches and steering motor via SNAC; with the defaults it plays the same as before. Includes the September 25 race-buzz and CPU timing fixes. The optional force-feedback wheel helper is not installed by this feed. Replaces the Cruis'n USA-only core; your Cruis'n USA saves are kept.

RBF: `blahm1d_vunit_20260926.rbf`

SHA-256: `b768a364b8df4f3587ea0c447961eb90f3f3b09595094dc276c10456d796f307`

Games: Cruis'n USA (rev L4.4); Cruis'n World (rev L2.5); Off Road Challenge (rev 1.63).

## V Unit - War Gods r16

Beta; cabinet verified; timing passed at all corners. War Gods booting from its original hard disk, with full-speed DCS2 sound; fights run at about 98% of arcade speed. Fixes the power-on test error "U28 VR ASIC failed polygon draw test (V+ DMA ASIC Error E2)". Credits and master volume now survive a power cycle. New Volume Up / Volume Down buttons, appended so saved button maps stay valid. You supply the disk image: run `chdman extracthd -i <War Gods CHD> -o wargods.img` and put it in `games/wargods/`; the feed installs `config/wargods.s0` once to mount it. OSD Audio Gain (default +12 dB) and Dither options.

RBF: `blahm1d_wargods_20260929.rbf`

SHA-256: `f3f2e6421179a3e8e8d27f93271800880b819ce5f4d8e7ca7a1b2a0ac66bb5ac`

Games: War Gods (HD 10/09/1996 - Dual Resolution).

## Saves after MRA renames

Every game now ends in ` [blahm1d]` (for example `Smash T.V. (rev 8.00) [blahm1d]`), so these games never collide with another collection's version of the same game. This is a one-time change.

MiSTer names a game's save (`config/nvram/<name>.nvm`) and DIP settings (`config/dips/<name>.dip`) after the game's entry name. To keep your high scores, settings and DIP switches, rename those files to the new name before first launching the renamed entry, e.g. `Smash T.V. (rev 8.00).nvm` to `Smash T.V. (rev 8.00) [blahm1d].nvm`. Older entries renamed earlier follow the same rule: `RevX_09132026` became `Revolution X [blahm1d]`, and `Narc (rev 7.00) [v22 erase row]` became `Narc (rev 7.00) [blahm1d]`. Your old files are never deleted by Update_All; factory defaults are installed under the new names only where you have none.

The newer Gladiator OSD and Legend of Kage CRT drafts have no corresponding binary; they are not represented as delivered features. Diagnostic Y Unit test-ROM and Wolf HUD-counter images are excluded. Wolf community-hack MRAs are excluded because their ROM sources are separate from the original MAME game sets.

All published MRAs retain the original game profiles and ROM load definitions. Only the core binding is namespaced; invalid double-hyphens inside XML comments are normalized where necessary.

## Night Slashers - v1.4 sprite fade fix

v1.4 sprite/special-attack fade fix; DDR3 sprite graphics and audio updates. Custom MRA ROM layout preserved. Known issues: title-screen starfield animation and occasional sprite edge wrap. No new FPGA build or cabinet test performed for this distribution.

RBF: `blahm1d_nightslashers_20260712.rbf`

SHA-256: `935380e3cc8297154a6d758d50295a279f1db9aeb664d2aef7ee2078b40f4498`

Games: Japan Rev 1.2; Korea Rev 1.3; Over Sea Rev 1.2.

Core by blahm1d, built on JTFRAME by Jose Tejada (jotego), with Amber CPU contributions. Original credits and GPLv3 license are preserved in the source archive.

## September 19 ROM-loading corrections

Ougon no Shiro now uses the Japanese ROM CRCs, the required text/graphics order, and all four MCU ROMs. Its 0x6D440-byte stream matches the published source memory map. It accepts ogonsiro.zip or the merged gladiatr.zip. NBA Maximum Hangtime also accepts merged nbahangt.zip. Both parent archives are indexed by the upstream ROM database. RBFs are unchanged; these metadata fixes have not been cabinet-tested.

Automatic ROM delivery still requires the upstream source registration and mirror sync: [PR #8](https://github.com/zakk4223/ArcadeROMsDB_MiSTer/pull/8). A merged source change alone is not a verified download.
