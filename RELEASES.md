# Release status - 2026-09-14

10 RBFs and 37 MRAs. No new FPGA build was performed for this feed.

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

## Wolf Unit - Flip window master

Beta; recorded timing pass. Seven original Wolf Unit games. Wider page-flip window; MK3 HUD flashing is not confirmed fixed. Community hacks requiring separate ROM sources are not installed by this feed.

RBF: `blahm1d_wolfunit_20260803.rbf`

SHA-256: `c3433178eb3bf9125b7342eab69f075f8e0a3f9649ce10040fc174a0eff26a6d`

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

## NARC - v22 erase row

Beta; retained cabinet candidate. NARC rev 7.00. Erase-band/refill-tag update; final HUD-row cabinet acceptance is not recorded.

RBF: `blahm1d_narc_20260803.rbf`

SHA-256: `40d52e01e5ee955520125302d8938bee080630829534cb3e56f0161908c59fd5`

Games: Narc (rev 7.00).

## T Unit - ADPCM S12 baseline

Beta; retained S12 baseline. NBA/TE scaling repair. Popup flashing, ADPCM sound/cold-boot issues and save persistence are unresolved. Newer S20/S22 cabinet-rejected builds are excluded.

RBF: `blahm1d_tunit_20260826.rbf`

SHA-256: `868825b1578997257b89cfa16e6d86a138f117219a969995e3a8eee0c7206bd0`

Games: Judge Dredd (rev TA1 7/12/92, location test); Mortal Kombat (rev 5.0 T-Unit 03/19/93); NBA Jam (rev 3.01 4/07/93); NBA Jam Tournament Edition (rev 4.0 3/23/94).

## T Unit - DCS S12 baseline

Beta; timing-clean S12 baseline. Mortal Kombat II. The later S19 timing-waived cabinet-only build is excluded. Audio reconstruction and save behavior remain under development.

RBF: `blahm1d_tunitdcs_20260826.rbf`

SHA-256: `fdcc772686781e201df519dc81d00de01ec7897cb33aee6b434799218c8023f6`

Games: Mortal Kombat II (rev L3.1).

## Selection notes

T Unit uses the retained S12 baselines because the later S20/S22 handoff rejects those builds for cabinet video/audio defects, and S19 DCS carries a timing waiver. These baselines still have documented limitations.

The newer Gladiator OSD and Legend of Kage CRT drafts have no corresponding binary; they are not represented as delivered features. Diagnostic Y Unit test-ROM and Wolf HUD-counter images are excluded. Wolf community-hack MRAs are excluded because their ROM sources are separate from the original MAME game sets.

All published MRAs retain the original game profiles and ROM load definitions. Only the core binding is namespaced; invalid double-hyphens inside XML comments are normalized where necessary.
