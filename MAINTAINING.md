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

## Required ROM-download coverage check

For every new core or RBF/MRA update, verify ROM-download integration as part of
release readiness. Update_All's Arcade ROMs option uses a separate database;
installing an MRA does not automatically register its ROM requirements there.

1. Compare all affected MRA ZIP references with the current Arcade ROMs database
   configured by Update_All. Preserve custom layouts and check parent/clone and
   ROM-version compatibility; a ZIP-name match alone is not a content/CRC check.
2. Confirm this distribution is in the upstream MRA source list. Check the
   [initial registration PR](https://github.com/zakk4223/ArcadeROMsDB_MiSTer/pull/8)
   and current upstream state before creating another submission. When needed,
   submit a tested source/index change from blahm1d as part of the authorized
   publication task.
3. Run the upstream metadata generator or equivalent coverage checks and record
   missing ZIPs, unresolved games, and any parent alternatives. Do not infer
   complete coverage merely from a successful generator exit.
4. Verify maintainer acceptance, mirror synchronization, and live database entries
   before saying automatic ROM delivery is available. An open PR is pending work.
   If core publication proceeds with gaps, name them explicitly in the handoff.
5. Verify the live core feed and a clean RBF/MRA download separately from ROM
   availability and cabinet behavior. No ROM payloads belong in this repository;
   a separate ROM-hosting/upload operation requires explicit authorization.

Use blahm1d for public author/committer identities, PRs, branch names, and
distribution URLs. Preserve original third-party license and copyright notices.

Existing registration may discover future MRAs automatically, but every new
set/version still needs the coverage checks above.
