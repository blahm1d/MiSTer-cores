# Publishing an update

Prepare and verify the exact release package and website draft first. Ask the
owner for approval before committing, pushing, updating an upstream PR, or
uploading to the live mirror. A request to prepare a release is not publication
approval. Pushing to `main` triggers the database publication workflow.

1. Select the intended release artifact and its matching MRA files. Preserve its
   build/cabinet evidence and known issues. Do not select an RBF solely by its date.
2. Put the RBF in `_Arcade/cores/` using its existing `blahm1d_<id>` prefix and a
   new `_YYYYMMDD.rbf` suffix. Update the corresponding MRAs. Every MRA name ends
   ` [blahm1d]` (so it never collides with another feed's MRA of the same game);
   MiSTer names the game's `.nvm` save and `.dip` file after it, so do not rename a
   shipped MRA without shipping its NVRAM default under the new name. Main games sit
   in `_Arcade/_Blahm1d/`, displayed as Arcade > Blahm1d; regional/revision variants of a
   main game go in `_Arcade/_Blahm1d/_alternatives/_<Game>/`. Keep the
   MRA game/profile/ROM layout matched to the core. Every folder name starts with
   `_`: MiSTer's menu hides `_Arcade` subfolders without it. Validation enforces this.
   Moving an MRA into this folder must preserve its filename and internal game name
   so existing NVRAM and DIP filenames remain valid. RBFs remain in `_Arcade/cores/`.
3. Update `catalog/releases.json` with the exact SHA-256 hashes, paths, build
   version, game list and status. Replace that core's previous downloadable RBF;
   Git history retains it for rollback. Update the matching source archive and
   `catalog/sources.json` with the corresponding source and license notices.
4. Run `python tools/build_db.py --validate-only`, then commit only the intended
   release files and push to `main`. Check the **Publish MiSTer downloader database**
   Actions run. A failed validation leaves the previously published feed in place.

5. Publish the mirror users download from (`https://mister.blahm1d.com`, the
   `blahm1d-mister` R2 bucket) after committing:
   `python tools/publish_r2.py --bucket blahm1d-mister --base-url https://mister.blahm1d.com`
   It uploads new payloads and source archives first, then the database and INI.
   Requires `wrangler login` on the publishing machine.

Use `tools/add_core.py --dry-run` for a new core and
`tools/stage_release.py --dry-run` for an existing core before staging its files.
Review the source snapshot and MRA changes, then run without `--dry-run` only
inside an isolated publishing checkout. `tools/publish_r2.py --dry-run` generates
the database and website and lists proposed uploads without uploading them.
After approved publication, run `tools/verify_mirror.py` against the public INI
and verify a clean Downloader installation and preserved saves separately.

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

## Game pages and search discovery

`tools/build_site.py` generates a page for every catalog game and core, plus the
developer profile, homepage, release notes, sitemap and `llms.txt`. Page URLs use
the stable MRA title, so different hardware profiles and game revisions remain
distinct. Visible attribution and structured data identify blahm1d as the FPGA
core developer/publisher while preserving original arcade and source credits.
Release status and known issues come directly from the catalog.

Preview and validate locally before approval:

```text
python tools/build_site.py --out dist/search-preview
python tools/verify_site.py --local-dir dist/search-preview
python tools/publish_r2.py --bucket blahm1d-mister --base-url https://mister.blahm1d.com --site-only --dry-run
```

After the owner approves publication, commit the website source changes, push,
then use the same command without `--dry-run`. `--site-only` publishes the site
without changing the RBF/MRA database. Both website-only and full publication
generate all current pages and automatically verify live page coverage,
attribution, structured data, links and sitemap after uploading. Obsolete local
preview files are excluded from uploads.

Google Search Console needs the site property verified and `sitemap.xml`
submitted once. New page URLs are added to that sitemap automatically on each
publication; users do not need to submit every game URL. Search Console access,
Google indexing and appearance in AI Overviews are separate from deployment.
No AI-summary placement or indexing guarantee is claimed.

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
   Record any pending registration or unresolved automatic coverage in the handoff.
   Describe ROM provision as Update_All or BYOR; no ROM payloads are included.
5. Verify the live core feed and a clean RBF/MRA download separately from ROM
   availability and cabinet behavior. No ROM payloads belong in this repository;
   a separate ROM-hosting/upload operation requires explicit authorization.

Use blahm1d for public author/committer identities, PRs, branch names, and
distribution URLs. Preserve original third-party license and copyright notices.

Existing registration may discover future MRAs automatically, but every new
set/version still needs the coverage checks above.
