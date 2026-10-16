# Source-to-showcase migration — Wheel & PlaySparse

**Status:** public showcase assets staged in the portfolio, **not** newly created standalone GitHub repositories. Existing original repositories are **still public** until their owner manually changes visibility through GitHub's repository settings.

## Safe migration sequence

1. **Inventory ownership and license obligations.** Check all original contributors, third-party dependencies, existing MIT notices, released artifacts, PRs and the project's history. Previously distributed MIT versions remain available under those rights, even if future versions are closed.
2. **Back up each original privately.** Clone/mirror all branches and tags to a safe local backup and verify the branch heads. Never strip history to pretend old public source never existed.
3. **Create two NEW public GitHub repositories** named `Wheel-showcase` and `PlaySparse-showcase` with blank histories (no templates, no fork). **Do not create them by forking or pushing from the old source repositories**.
4. **Copy only vetted showcase assets** (README, screenshots, landing-page HTML, notices and contact information), without original application source code or Git history. This portfolio's `showcases/wheel` and `showcases/playsparse` folders provide the staged material.
5. **Review license notices** before adding any new license. Avoid describing MIT-origin code as if proprietary redistribution rights were retroactively canceled. Be precise about photo/logo rights.
6. **Test the public showcases.** Check real screenshots, mobile readability, working links and no credentials, sourcemaps, code packages or hidden source files.
7. **Handle open pull requests and integrations.** Record/close or reconcile old source PRs, verify Actions artifacts and releases, update cross-links, and plan how GitHub Actions/private submodules will work after the change.
8. **Owner action:** GitHub → original repository → **Settings → General → Danger Zone → Change repository visibility → Make private**. Verify that GitHub plan/organization restrictions permit the change. This may disable Pages or alter Actions/third-party consumers and is not reversible in effect for existing external clones.
9. **Verify after cutover.** From an unauthenticated session, the original code should be inaccessible while `Wheel-showcase` and `PlaySparse-showcase` remain publicly viewable. Check profile links, public release archives, images and any separate package registries.
10. **Keep private development in original repositories.** Publish only sanitized, reviewed demonstration assets and forward-looking public claims.

## What private does not do

- It does **not** revoke existing MIT licenses or erase public forks/previously copied source.
- It does **not** automatically remove copies in package registries, third-party caches, releases, containers or public backups.
- It does **not** grant ownership of other people's contributions.
- It does **not** guarantee a desktop binary cannot be reverse engineered.

## Manual constraints this automation could not perform

The current GitHub connector supports source reads, file commits, branches and pull requests, **but has no supported create-repository or change-repository-visibility action**. These require an account owner to use the GitHub UI (or a separately authorized administrative client). Do not claim the two source repos are already private.

## Cutover sign-off checklist

- [ ] Contributor/IP rights reviewed
- [ ] Backup of all branches/tags verified
- [ ] Two clean public showcase repositories created
- [ ] Showcase files copied; no sensitive source/history
- [ ] Screenshot rendering and email links checked
- [ ] Old PRs, CI, pages, badges and releases reviewed
- [ ] Original repositories deliberately switched to Private by owner
- [ ] Unauthenticated access tested after visibility changes
