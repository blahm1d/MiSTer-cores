# Release status - 2026-09-24

11 RBFs and 40 MRAs. September 23-24 updates: Wolf Unit, NARC and T Unit DCS.

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

## Wolf Unit - Flip fence + DCS sound fix

Beta; cabinet verified. Seven original Wolf Unit games. Page flip now waits only for the old page's DMA commands, fixing MK3/UMK3 Motaro/Kintaro/Shiva HUD and sprite flashing. DCS audio 16x polyphase output filter (hiss fix). Timing waiver: misses only the slow -40C corner by 0.041 ns on the HDMI scaler clock. Community hacks requiring separate ROM sources are not installed by this feed.

RBF: `blahm1d_wolfunit_20260924.rbf`

SHA-256: `024cc539ac9810545017268b9e75df81cb9706b0ab55e5a92304f64e9cc1d226`

Games: Mortal Kombat 3 (rev 2.1); NBA Hangtime (L1.3 10/10/96); NBA Maximum Hangtime (L1.03 06/09/97); NHL Open Ice: 2 on 2 Challenge (rev 1.21); Rampage: World Tour (rev 1.3); Ultimate Mortal Kombat 3 (rev 1.2); WWF: WrestleMania (rev 1.30 08/10/95).

## Y Unit - Family r36

Beta; four-corner timing passed. Smash TV, Trog, High Impact, Super High Impact, Strike Force and Saurian Front. Background/erase and Smash TV sound-memory changes; cabinet confirmation pending.

RBF: `blahm1d_yunit_20260904.rbf`

SHA-256: `c58d851299b633d2c4d19d3e907627eb500e0130442e21f0bd983bf3303c7418`

Games: High Impact Football (rev LA5 02/15/91); Saurian Front (proto v5.0 08/07/90); Smash T.V. (rev 8.00); Strike Force (rev 1 02/25/91); Super High Impact (rev LA2 10/22/91); Trog (rev LA5 3/29/91).

## Y Unit - ADPCM / T2 guns r41

Beta; four-corner timing passed. Mortal Kombat Y Unit, Terminator 2 and Total Carnage. Per-player guns, Sinden border and crosshair controls; cabinet verification pending.

RBF: `blahm1d_yunitadpcm_20260905.rbf`

SHA-256: `2061a3031fbf5d3878a79eccb912b84336ad976dfabc80d2cddb84f931745b41`

Games: Mortal Kombat (rev 4.0 09/28/92, Y-Unit); Terminator 2 - Judgment Day (rev LA4 08/03/92); Total Carnage (rev LA1 03/10/92).

## X Unit - Revolution X clean audio/performance

Beta; physical signoff passed. Revolution X. Separate Music/SFX volume controls and DMA performance changes. No diagnostic overlay; latest whole-core gameplay and cabinet verification remain pending.

RBF: `blahm1d_xunit_20260914.rbf`

SHA-256: `1e8b5ed7ad312649ae04fb1669557dc1d1ebc15ff65dc1830012b4aa647fb67e`

Games: Revolution X.

## Exidy cores - Exidy 440 r6

Beta; four-corner timing passed. Eleven Exidy 440 games. Core family bring-up; first cabinet validation pending.

RBF: `blahm1d_exidy440_20260907.rbf`

SHA-256: `b56e3467b5863e48cd89a8256a3ab134f3df60c6f94b201f0663ae988da5e116`

Games: Catch-22; Cheyenne; Chiller; Clay Pigeon; Combat; Crackshot; Crossbow; Hit 'n Miss; Showdown; Top Secret; Who Dunit.

## NARC - v23 HUD row

Beta; cabinet verified. NARC rev 7.00. The gameplay erase band now ends at row 229, removing the garbage row at the bottom of the top HUD. Timing passed at all corners.

RBF: `blahm1d_narc_20260923.rbf`

SHA-256: `887cd88ed3175ebf3ca680130179ff664a3b260b903459b1d604177c1f19dccb`

Games: Narc (rev 7.00).

## T Unit - ADPCM S12 baseline

Beta; retained S12 baseline. NBA/TE scaling repair. Popup flashing, ADPCM sound/cold-boot issues and save persistence are unresolved. Newer S20/S22 cabinet-rejected builds are excluded.

RBF: `blahm1d_tunit_20260826.rbf`

SHA-256: `868825b1578997257b89cfa16e6d86a138f117219a969995e3a8eee0c7206bd0`

Games: Judge Dredd (rev TA1 7/12/92, location test); Mortal Kombat (rev 5.0 T-Unit 03/19/93); NBA Jam (rev 3.01 4/07/93); NBA Jam Tournament Edition (rev 4.0 3/23/94).

## T Unit - DCS sound fix

Beta; timing passed at all corners. Mortal Kombat II. DCS audio 16x polyphase output filter (hiss fix). Cabinet confirmation not yet recorded; save behavior remains under development.

RBF: `blahm1d_tunitdcs_20260923.rbf`

SHA-256: `f7c8861da1a6105809e73cc77de452fea8bc5273989f429519eb2eb19b8c7574`

Games: Mortal Kombat II (rev L3.1).

## Selection notes

T Unit ADPCM uses the retained S12 baseline because the later S20/S22 handoff rejects those builds for cabinet video/audio defects. T Unit DCS moved from the S12 baseline to the September 23 sound-fix build. These builds still have documented limitations.

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
