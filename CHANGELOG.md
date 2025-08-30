# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.31.0] - 2025-08-29

### Added
- New `Modules/DbCache` Mongo cache
- New `Modules/HealthCache` health check cache

---

## [0.30.0] - 2025-08-22 

### Added
- Local P2Pool deployment

---

## [0.29.0] - 2025-08-20

### Fixed
- BugFix: Fixed Db4ESystemD status()

### Changed
- Moved update operations from the TUI to the server using the JobQueue

### Added
- Dynamic buttons for MoneroDRemote, P2PoolRemote and XMRig
- Implemented enable/disable for XMRig
- Implemented a Trans Log to show TUI operation history
- Implemented Trans Log entries for new operations

---

## [0.28.0] - 2025-08-17

### Fixed
- `db4e-server`: set __version__

### Changed
- Removed `Modules/ConfigMgr/Config` - Replaced the config object with direct references to the default values
- Major refactor: Replaced dictionaries with classes
- Implemented a client/server JobQueue

---

## [0.27.2] - 2025-08-04

### Fixed
- Error in `pyproject.tomli` file

### Added
- Sceenshot of the Db4E installer

--- 

## [0.27.0] - 2025-08-04

**Skeleton Db4E Server**

### Added
- New `Modules/Db4eLogger` module to handle logging to file and to MongoDb
- New `db4e/server.py` to house the systemd Db4E server code
- New `vendor_dir/db4e/logs/db4e.log` file
- Connected the systemd `db4e.service` directly to `db4e/server.py`

---

## [0.26.1] - 2025-08-04

### Changed
- Updated screenshot of the Db4E console on the [website](https://db4e.osoyalce.com/pages/db4e-tui.py.html)

---

## [0.26.0] - 2025-08-04

### Added
- CRUD operations for XMRig deployments

### Changed
- Huge refactoring of the backend, thus the long delay between releases

### Fixed
- UI look and feel
- Error handling

---

## [0.25.1] - 2025-07-18

### Fixed
- XMRig > New > crash

---

## [0.25.0] - 2025-07-18

### Changed
- Refactor code to improve efficiency and better styling and layout

---

## [0.24.1] - 2026-07-16

### Fixed
- Fixed NavPane unicode.

---

## [0.24.0] - 2025-07-16

### Added
- New `Modules/HealthMgr` module to perform health checks
- New constants in `Labels` and `Fields` to support health checks
- New `is_port_open` and `is_valid_ip_or_hostname` functions to support health checks
- New detailed health check results in `MonerodRemote`, `P2PoolRemote` and `XMRig` panes

### Changed
- Changed background of `Static` and `Tree` widgets to black
- Added support for health checks to `Db4eApp`, `Widgets/NavPane` and `DeploymentMgr`

### Fixed
- Minor tweaks to `Db4E.tcss`

---

## [0.23.2] - 2025-07-15

### Added
- Generate a XMRig configuration file in `Modules/ConfigMgr`
- Add a call to `ConfigMgr:gen_xmrig_config()` to `Modules/DeploymentMgr`
- Added a read-only field, `Configuration`, to the `XMRig` pane showing the full path to the config file
- Created `ConfigMgr:del_config()` to delete a configuration file and return results

### Changed
- Refactor InitialSetup pane to use compose instead of set_data + mount
- Refactor Db4E to use compose instead of set_data + mount
- Modified `Modules/DeploymentMgr` to update the XMRig configuration file if
- the XMRig instance changes or if it's reconfigured to use a different P2Pool deployment

### Fixed
 Set read-only Db4E fields to be read-only

---

## [0.23.1] - 2025-07-16

### Added 
- Unicode to brighten up the NavPane


### Added
- Split the flow to route remote deployments to remote panes
- Added P2PoolRemote and MonerodRemote panes to handle the split
- Added additional constants to support the split
- Added additional message routes to support the split"

### Changed
- Minor code refactoring improvements
- Removed `Db4E.tcss` styling redundancies

### Fixed
- If Db4e vendor_dir updated, update the directory on the filesystem
- Properly update the user_wallet and vendor directory in the DB

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
