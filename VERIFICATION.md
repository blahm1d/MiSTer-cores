# Downloader verification - 2026-09-14

The initial public collection contains **10 RBFs, 37 MRAs and 2 optional factory
NVRAM defaults**. There are no game ROM files in the collection.

MiSTer Downloader source revision
`5d0771359ae396aaea64453e6791ac87781d78f4` was used to verify:

- Its own database/path/URL validators accept the generated database.
- The INI is discovered automatically as a drop-in and preserves the default
  MiSTer distribution configuration.
- The actual downloader installs the public GitHub payloads in a fresh temporary
  SD-card folder. All 10 RBFs, 37 MRAs and the absent Total Carnage default matched
  the published sizes and hashes.
- An existing Revolution X save and an unrelated core remained unchanged.
- A second updater run exited successfully and rewrote none of the payloads.
- All published MRA core bindings resolve to the intended namespaced RBF.
- Source archives passed ZIP integrity, file-hash and credential-signature checks.

The GitHub Actions database publication succeeded. These are downloader/package
checks, not new FPGA builds, ROM downloads, hardware tests or cabinet acceptance.
See [RELEASES.md](RELEASES.md) for each core's separate engineering status.
