# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.42.1] - 2025-20-03

### Fixed
- Added the correct bundled p2pool.
- Fixed the case where there are no uptime record yet.

---

## [0.42.0] - 2025-10-03

### Added
- Added a `deployment_dir/db4e/logrotate` directory to house logrotate files.
- Added logrotate templates for local `XMRig`, `P2Pool` and the `Db4E` deployment.
- Updated the`/etc/sudoers.d/db4e` file:
  - Allow user to run `logrotate` as root (required for XMRig logs).
  - Allow user to run `chown` command on the logrotate files (xmrig log files are owned by root).
- Added a `gen_logrotate_config()` methods to `P2Pool`, `XMRig` classes.
- Added a `_gen_db4e_logrotate_config()` method to the `InstallMgr`.
- Created a new `LogRotateConfig` `Component` class.
- Added `max_log_files()`, `max_log_size()` and `logrotate_config()` methods and components to `XMRig` and `P2Pool`.
- Added a banner to the `/etc/sudoers.d/db4e` file.
- Added *logrotate* definitions to the `DFile` and `DDir` constants files.
- Added a `DeplMgr:get_dir(DDir.LOGROTATE)` method.
- Added a *P2Pool uptime* check before adding *Miner hashrate* records to avoid adding invalid, super-high hashrates when P2Pool first starts.
- Implemented formal *Remote XMRig* deployment records.
- Wrapped `P2PoolWatcher` functions in *try/except* blocks where exceptions are logged.
- Upgraded bundled `P2Pool` to v4.11

### Fixed
- Configured the *Hashrate* button visibility so it's not visible for the *New* screens.
- Passed `P2PoolWatcher` the *Db4E* log file instead of the P2Pool log file.
---

## [0.41.0] - 2025-09-30

### Added
- `OpsDb` to support operations to the *ops* Mongo collection:
  - `get_ops_events()` - Return start/stop events
  - `add_start_event()` and `add_stop_event()` - Add start/stop events
  - This module creates `start_stop_event`, `current_uptime` and `total_uptime` Mongo documents to track the current and cumulative uptime of the various components.
  - Added a *Runtime Log* item to the `NavPane` that shows timestamped *start/stop* events.
  - Added a *Uptime* button to the *Db4E Core* pane to show cummulative and current uptime of the various components.
  - Added `Runtime` pane.
- Added `ChainPane` and `ChainHashrates` panes.
- Added `XMRigHashratesPane`
- Added a `DOps` contants file.
  
### Changed
- Removed the `DbCache` from the `DeplMgr`, it now does direct database operations.
- Moved the `enabled` boolean in the Mongo deployment records into `Components`.
- Removed redundant parameters to the various `InstallMgr` functions.
- Changed the inheritance hierarchy for `Monerod`, `P2Pool` and `XMRig` classes, they used to inheirit from `LocalSoftwareSystem`, now they inheirit from `SoftwareSystem`.

### Fixed
- Internal `P2Pool` startup and shutdown based on the selection (or disable) of the *primary server*

### Removed
- Unused `PlotViewPane`

---

## [0.40.0] - 2025-09-27

### Added
- Added a *Status* sub-title to the various panes' health check box.
- Added a *Runtime* log to track the uptime of the various components.
- Added a *Runtime* item to the NavPane to expose the log.
- Added an *Instance* field to multiple Mongo mining metrics records
- Added a `DSelect` constants file.

### Fixed
- Disabled pan and zoom for HashratePlot widget, it's not helpful.
- Removed unused `tmpl` (Templates) Mongo collection.
- Fixed layout issue with the `Db4E` pane.

### Changed
- Renamed *ops* Mongo collection to *jobs*
- Moved `DbMgr:get_jobs()` to `JobQueue`
- Renamed *Analytics* to *Hashrates* for the pane titles, buttons and functions.

--- 

## [0.39.0] - 2025-09-26

### Changed
- Replaced `textual-plotext` wrapper class with native `textual-plot`
  - Moved date selection into a separate box on the analytics panes
  - Fixed `Hashrate` metric in analytics panes

---

## [0.38.1] - 2025-09-25

### Added
- Health checks for *Internal P2Pool* deployments, in the `NavPane` and `HealthMgr`
- Added a *View Log* button to the *Internal P2Pool* pane

### Changed
- *Chain Stats* tree layout in the `NavPane`
- Replaced `textual-plotext` wrapper class with native `textual-plot`
- Modified the output of `MiningETL.get_hashrates()` for `textual-plot`

### Removed
- Removed `PlotViewPane`: Plot views are integrated into  existing panes
---

## [0.38.0] - 2025-09-21

### Added 
- Major refactoring of how contants are handled:
  - Added `DDebug`, `DDef`, `DDir`, `DElem`, `DField`, `DFile`, `DForm`, `DJob`, `DLabel`, `DMethod`, `DMining`, `DModule`, `DMongo`, `DPane`, `DPlaceholder`, `DStatus` classes to hold constants.
  - Removed `Buttons`, `Defaults`, `Fields`, `Jobs`, `Labels`, `Panes`, `SystemdTemplates`
- Added new classes to `Components`:
  - `BlockchainDir`, `Hashrate`, `P2PPort`, `PrimaryServer`, `StatsMod`, `StdinPath`, `Timestamp`, `Uptime`.
  - Removed `ObjectId`.
- Added three internal P2Pool deployments as part of the install to collect metrics for the *Main*, *Mini Sidechain* and *Nano Sidechain*
- Added a `MiningDb` and `P2PoolWatcher` modules to collect metrics from the user defined and internal *P2Pool* deployments.
- Stubbed out a `PlotDb` module as part of the *Data Abstration Layer*
- Added a new `XMRigRemote` class to encapsulate remote miners
- Added a `XMRigRemotePane` to display collected information about detected remote miners

### Changed
- Refactor of `DbCache` and `HealthCache`.
- Refactor of class relationships, see:
  - https://db4e.osoyalce.com/images/App-Relationships.png
  - https://db4e.osoyalce.com/images/Server-Relationships.png
- Refactored the `Modules\DeploymentMgr` into `DeplClient` and `DeplMgr`
- Changed the left-hand `NavPane`:
  - To use a single *Textual* tree
  - Included remote miners that are detected; no user action required
- 

### Fixed
- Fixed paths in the `Templates/p2pool-4.9.1/systemd/p2pool@.service` file to actually create a functional STDIN pipe for the running P2Pool service


---

## [0.35.0] - 2025-09-04

### Added
- Added a *restart* operation to restart a local deployment when the configuration changes
  - Automatic restart of local Monero and P2Pool deployments if the configuration changes
  - Added a *restart* constant to `Constants/Jobs`
  - Added `server:restart(job)` to restart a local deployment
- Extended `DeploymentMgr:get_dir()` to return the versioned *Monero*, *P2Pool* and *XMRig* directories
- Added a feature to disable downstream systems
  - Added `DbCache:get_downstream()` to return downstream *P2Pool* and *XMRig* instances
  - Added `server:disable_downstream()` to disable downstream *P2Pool* and *XMRig* instances
  - Added supporting `DeploymentMgr:get_downstream()`
- Added `DeploymentMgr:get_template()` to return *XMRig*, *P2Pool* and *Monero Daemon* templates
- Updated and added additional `Constants/Labels`
- Added `DeploymentMgr/post_job()`
- Added `Job:add_msg()` function

### Changed
- Changed `JobQueue:post_job()` to accept a *job* instead of a dictionary
- All deployment panes to use `post_job` for *enable*, *disable* and *update* operations
  - Updated `Job:to_rec()` to support the above change
- Renamed *Trans Log* to *Console Log* in the NavPane 
- Colorized the *console log* contents in `TUILogPane`
- enhanced the message content by 

### Fixed
- Removed uneeded *run* from the `InstallMgr:_make_p2pool_dir()`
- Fixed bug where the Initial install proceeded even though the vendor dir was invalid
- Removed unnused `set_component_value()` and `gen_radio_button()` from `Modules/Helper`
- Fixed reference bug in `DbCache/get_downstream()`
- Enforced unique instance names
- Made instance name immutable for all deployments

---

## [0.34.0] - 2025-09-02

### Added
- Added local *Monero Daemon* health checks to `Modules/HealthMgr`
- Added local *Monoro Dameon* logs to the TUI

### Changed
- Merged the *Metrics* and *Deployments* trees in the `Widgets/NavPane`
- Upgraded bundled XMRig to freshly compiled version v0.24.0
- Replaced custom compiled *Monero Daemon* with a more portable version from GetMonero.org
- Upgraded backend Textual from 4.0.0 to 6.0.0

### Fixed
- Paths to P2Pool.socket in the systemd configuration file were corrected
- Fixed crashes caused by upstream components being deleted
- Removed unneeded *run* dir for the P2Pool deployment

---

## [0.33.0] - 2025-09-01

### Added
- Additional `Constants/Defaults` and `Constants/Fields`
- Minor additions to the `Db4E.tcss` for styling
- Support for local *Monero Daemon* deployments in the `Modules/DeploymentMgr`
- Fleshed out the `Modules/MoneroD` class
- Created a form in the `Panes/MoneroDPane`

### Changed
- Updated constructor for `Modules/Db4ESystemD`
- Switched the `Panes/LogViewer` to use native Textual Log widget
- Upgraded the bundled `Monerod` to v0.18.4.2

### Fixed
- A bug in the `Panes/LogViewer` that cause lockups and app freezes

---

## [0.32.0] - 2025-08-31

### Added

- New `Panes/LogViewPane` for viewing log files in the TUI
- New tree navigation for viewing the logs
- Upgraded bundled P2Pool to 4.9.1
- Added constants to `Defaults`, `Fields`, `Labels`, and `Panes`
- Created a `Components/Logfile` class
- Added `LogFile` to local `Monerod`, `P2Pool` and `XMRig` classes
- Added the new `LogViewPane` to the `Modules/MessageRouter` and `Modules/PaneCatalogue`

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
