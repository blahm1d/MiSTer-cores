# Publishing an update

1. Select the intended release artifact and its matching MRA files. Preserve its
   build/cabinet evidence and known issues. Do not select an RBF solely by its date.
2. Put the RBF in `_Arcade/cores/` using its existing `blahm1d_<id>` prefix and a
   new `_YYYYMMDD.rbf` suffix. Update the corresponding MRAs under
   `_Arcade/_blahm1d/`. Keep the MRA game/profile/ROM layout matched to the core.
3. Update `catalog/releases.json` with the exact SHA-256 hashes, paths, build
   version, game list and status. Replace that core's previous downloadable RBF;
   Git history retains it for rollback. Update the matching source archive and
   `catalog/sources.json` with the corresponding source and license notices.
4. Run `python tools/build_db.py --validate-only`, then commit only the intended
   release files and push to `main`. Check the **Publish MiSTer downloader database**
   Actions run. A failed validation leaves the previously published feed in place.

The workflow publishes `db.json.zip` and the downloadable INI to the `db` branch.
Every payload URL pins the source commit, so a database cannot silently mix old
metadata with new file contents. The database ID is permanently `blahm1d`.

RBF and MRA entries share a per-core `tangle` identifier. Downloader retains an
older entangled version if a replacement download fails. Existing NVRAM entries
use `overwrite: false`; never change that setting on users' saves.

This repository and its workflow do not build FPGA cores. Synthesis, timing,
assembly and cabinet qualification happen in the core's development workflow.
Do not add ROMs, CHDs, keys, private saves, personal configuration or development
logs to this distribution repository.

The feed format follows the official [custom database specification](https://github.com/MiSTer-devel/Downloader_MiSTer/blob/main/docs/custom-databases.md).
