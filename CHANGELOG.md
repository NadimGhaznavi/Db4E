# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.23.0] - 2025-07-15

### Changed
- Streamlined the code in the `MonerodRemote`, `NewMonerod` and `NewMonerodType` panes. 
- Reused some `Db4E.tcss` tags between panes

---

## [0.22.2] - 2025-07-14

### Fixed
- Updated poetry lock file to support upgrade of Textual to v4.0.0

---

## [0.22.0] - 2025-07-14

### Added
- Added logic to `App` to support new *XMRig deployment*
- Added a `Panes/NewXMRig` pane
- Added a route to `Modules/MessageRouter` for adding a new XMRig deployment
- Added an entry to the `Modules/PaneCatalogue` for adding a new XMRig deployment
- Added additional constants to `Constants/Fields`, `Constants/Labels` and `Contants/Panes`
- Added support for new *XMRig deployment* to `DbMgr`, `DeploymentMgr`, `Helper`, `MessageRouter` and `PaneCatalogue` modules
- Updated `NewMonerod`, `NewP2Pool`, `NewP2PoolType`, `P2PoolRemote` and `XMRig` panes

### Fixed
- Fixed `Panes/NewP2PoolType` layout in `Db4E.tcss`

---

## [0.21.0] - 2025-07-12

### Added
- Added styling to `Db4E.tcss` for new P2Pool panes
- Added additional constants to `Labels`, `Fields` and `Panes`
- Added `delete_one` to `Modules/DbMgr` for CRUD
- Added `NewP2Pool`, `NewP2PoolType` and `P2PoolRemote` panes
- Added `delete` for 'Remote Monero Daemon Deployments' in `DeploymentMgr`
- Added support for 'Remote P2Pool Deployments' to `DeploymentMgr`

### Changed
- Removed async / await from the codebase.
- Minor refactoring of `Welcome` and `Results` panes
- Changed `InitialSetup`, `MonerodRemote`, `NewMonerodType` form structure for the architectural changes to the `Modules/MessageRouter`
- Major architectural change in `Modules/MessageRouter` to support additional routing based on 'component' parameter

### Fixed
- Removed unused themes from `App`
- Formalized and cleaned up `initialization` logic in the app and the components

---

## [0.20.0] - 2025-07-11

### Added
- Added new constants to `Constants/Labels`, `Constants/Fields` and `Constants/Panes`

### Changed
- Minor refactor of `Panes/NewMonerod` and `Panes/Db4E`; Replaced positional parameter with named parameters
- Added support for "Edit Remote Monero Daemon Deployment" flow
- Updated `Db4E.tcss` to support layout and styling for "Edit Remote Monero Daemon Deployment"
- Updated `Modules/DbMgr`, `Modules/PaneCatalogue`, `Panes/MonerodRemote`, `Widgets/NavPane` to support "Remote Monero Daemon Edit" flow

### Fixed
- Removed duplicate successful Modules/DeploymentMgr results message

---

## [0.19.1] - 2025-07-10

### Changed
-Updated README

---

## [0.19.0] - 2025-07-09

### Added
- Additional constants in `Constants/Labels`, `Constants/Fields`, and `Constants/Panes`

### Changed
- Fully replaced magic strings with constants in `Widgets/NavPane`; complete refactor for clarity and maintainability
- Replaced magic strings with constants in `Modules/MessageRouter`; added `DeploymentMgr:new_deployment` registration
- Refactored `App` to support end-to-end "Remote Monero Daemon Deployment" flow
- Updated `Db4E.tcss` to support layout and styling for "Remote Monero Daemon Deployment"
- Updated `DbMgr`, `DeploymentMgr`, `InstallMgr`, `MessageRouter`, and `PaneCatalogue` to support the new deployment type
- Enhanced `Widgets/NavPane` to display and control "Remote Monero Daemon Deployment" instances

### Fixed
- `App` now correctly calls `PaneMgr.set_initialized(True)` after `InstallMgr.initial_setup()` completes

---

## [0.18.2] - 2025-07-09

### Added
- Workflow to manually trigger a rebuild of the project's Jekyll site

### Changed
- Added a link to an updated 'Getting Started' page
- Added information on triggering the Jekyll site rebuild in the Git 'Branching Strategy' page

---

## [0.18.1] - 2025-07-09

### Added
- Adopting a new `pages/Git-Commit-Standard` 

### Changed
- Updated the Getting Started page
- Moved the Mongo install howto

---

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
