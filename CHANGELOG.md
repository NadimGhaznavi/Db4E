# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.18.2] - 2025-07-09

## Added
- Workflow to manually trigger a rebuild of the project's Jekyll site

## Changed
- Added a link to an updated 'Getting Started' page
- Added information on triggering the Jekyll site rebuild in the Git 'Branching Strategy' page

## [0.18.1] - 2025-07-09

### Added
- Adopting a new `pages/Git-Commit-Standard` 

### Changed
- Updated the Getting Started page
- Moved the Mongo install howto

## [0.18.0] - 2025-07-08

### Added
- Installer fully implemented and now works end-to-end
- Introduced and maintaining a formal changelog (`CHANGELOG.md`)
- `DeploymentMgr.get_new_rec()` now calls `DbMgr.get_new_rec()` and returns the result
- New constants added to `Constants/Labels`, `Constants/Fields`, and `Constants/Defaults`
- `tests/conftest.py`: added fixtures and `has_message()` helper
- `Panes/Welcome.py`: added introductory content

### Changed
- `InstallMgr.initial_setup()` refactored into multiple smaller, testable functions
- Replaced magic strings with constants in `App.py`, `Panes/Db4E`, and `Panes/InitialSetup`
- Installer now uses the effective GID of the current user instead of prompting for a group
- `pages/Git-Branching-Strategy`: updated to include `CHANGELOG.md` in the release process
- Added comprehensive tests for `Modules/test_InstallMgr.py`

### Fixed
- Documented resolution steps for `pyproject.toml` merge conflicts during release
