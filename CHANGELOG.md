# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [Release 0.49.0] - 2026-07-31 20:03


- Setup per user `__pycache__` directory creation to avoid clashes between `Db4EClient` and `Db4EServer`

## [Release 0.48.9] - 2026-06-06 14:17 - Push to PROD

- Now running **Db4E** to run my PROD monero daemon

---

## [0.48.6] 2026-04-28 @ 08:19 - Ongoing Refactoring

### Added
- **Db4E Installation Flag**
  - Created a config file to store the "installation successful" flag
  - Passed to the Nav Pane so it knows what to display
  - Added `Db4EClient` `load_config()`, `save_config()`, `db4e_installed()` methods
- Added `Db4EClient:sudo_failed()` method
  - Passed to the Nav Pane so it knows what to display
- Added a health check for the core Db4E service to see if a primary server has been defined
- The deployment name to the *Internal P2Pool* health check message
- New `helper:get_upstream()` helper function
- Add a *ping* function to the `APIMgr` so the installer can check that the service has started up before trying to add the *Db4E* and *Internal P2Pool* instances
- Added a *Log View* feature and implemented it for the local *Internal P2Pool* and *MoneroD* deployments.
  - The button on the deployment view pane now has a *View Log* button, pressing it causes
  - the TUI to send a request to the *Db4E Service*, which retrieves the last 100 lines of the specified deployment log file and returns it to the *Db4E Client*
  - The log is displayed in a `LogViewPane` which also has a *Refresh* button and a drop-down menu that allows the user to refresh the log file and choose the number of lines to retrieve: 100, 250, 500, or 1000.

### Changed
- **Architectural Shift**
  - The *Db4E* service will now run as root.
  - The *install directory* will now be `/opt/Db4E`
  - Created a `db4e-create-install-dir.sh` script that runs with `sudo` access
  - Updated the following to reflect these changes.
    - *Initial Setup* screen 
    - `BootstrapMgr`
    - `SQLDb`
  - Removed the bootstrap file that contained the install directory
- Moved the `HealthMgr` and `HealthClient` into a new `health` folder
- `ChainPane`: Refactored button press handling code

### Fixed
- Made the wording in the *Initial Setup* screen consistent.
- Fixed `TUILogPane` formatting bug

### Removed
- Removed upstream monero field from the *Chain Pane* as that info is in the health messages

---

## [0.48.5] - 2026-04-16 @ 11:22 - Sudo Pre-Req test implemented

### Added
- Created new `util/SudoTest.py` and hooked it into the `Db4EClient` and `NavPane` to ensure that the sudo requirements are met before proceeding with the install.

---

## [0.48.4] - 2026-04-03 @ 18:33 - HOTFIX Update PyPI publishing workflows

### Added
- A step to install system dependencies for libsystemd, which is required for pystemd.

---

## [0.48.3] - 2026-04-03 @ 18:14 - SystemD Refactor Release"

### Added
- `HealthMgr` and "HealthDb` functions and updated some classes to use them
  - `Db4E` and `InternalP2Pool`
  - Status health reflected in NavPane elements

### Changed
- Refactored `Db4ESystemD` to use pystemd.
- Refactored the *healh check table* creation process
- Upgraded P2Pool

### Fixed
- Internal P2Pool instantiation process in `InstallMgr`

## [0.48.2] - 2026-03-28 @ 12:51 - Catchup Release

### Added
- Added a `tui_log` table to the `SQLdb:init_db` method and to the `pages/Schema` page.
- Added a `TUILogMsg` class to encapsulate a TUI log record.
- Added an `internal_p2pool` table to the `SQLmgr:init_db` method and to the `pages/Schema` page.
- Added `BaseMonero` and `BaseP2Pool` classes.
- Added `aiofiles` to `pyproject.toml` to support the migration of `P2PoolWatcher` from a *threaded* to an *asyncio* model.
  - Updated `poetry.lock` file.
- Added *sphinx* documentation generator:
  - Installed pip meta package to generate documentation.
  - Updated the core `conf.py` to parse code for inline documentation.
  - Added a *GitHub Pages* workflow to automatically generate documenation when when a new release is cuts.
- Added timestamp data to the `CurrentUptime` class to enable client/server data syncs.
- New `APIMgr` class that uses `fastapi` and `uvicorn` to enable client/server communication:
  - Data syncs between the `client.db` and `server.db`.
- Implemented a client/server database sync process.
  - *Db4E* client owns a `client.db`, *Db4E* service owns a `server.db`.
  - Implemented a sync using `uvicorn` and `fastapi`.
- Added `initialize()` functions to call `_init_db()` for `OpsDb`, `DeplDb` and `MiningDb`.
- Added a `status()` function to `BaseP2Pool` class.

### Changed
- Replaced the `DeplMgr:get_dir()` with `BootstrapMgr` module's `get_dir()` and `get_file()` functions.
- Changed the `LOG_ROTATE_CONFIG` constant to `LOGROTATE_CONFIG` in the `DDef` and `DField` constants files.
  - Changed backend `p2pool` and `xmrig` table's `log_rotate_config` to `logrotate_config`
  - Updated the `__dict__` and `__init__` methods in the `P2Pool` and `XMRig` classes.
  - Updated the `Components:LogRotateConfig` class.
- Completed conversion of the `InstallMgr` to use the new `SQLDb` and `BootstrapMgr` modules.
- Modifed `MessageRouter` and `InstallMgr` to use the *Console Log* pane to show install results.
- Complete rewrite of the `DeplMgr` module as part of the shift from **Mongo** to **SQLite3**.
- In `Db4ESystemD`, replaced the Mongo *ops* collection, with inserts of `StartStopRec` into SQLite `start_stop` table.
- Modified `SQLMgr:init_db()` to add `UNIQUE` constraints to the *hourly* records.
- Modified `SQLMgr:insert_one()` to handle the *hourly* record tables using the new constraint.
- Complete re-write of `MiningDb`: Migrated from Mongo `MiningDb` to SQLite `SQLMgr`.
- Update of `P2PoolWatcher` to match changes in `MiningDb`.
- Replaced all of the `InitialInstall` messages that were sent to a transient `Results` pane to the *Console Log* pane.
- Complete rewrite of the `TuiLogPane` parsing logic to reflect the new backend.
- Refactored `Db4e`, `MoneroD`, `MoneroDRemote`, `P2Pool`, `P2PoolRemote` and `XMRig` classes.
- Complete rewrite of the `DeplMgr` module to use the new backend.
- Converted the `P2PoolWatcher` module from a threaded model to an asyncio model.
  - Also replaced `time.sleep()` with `asyncio.sleep()` and `open()` with `aiofiles.open()`.
- Upgraded `Textual` from 6.0.0 to 6.4.0.
- Moved *Mgr* classes into a `mgr` folder. Renamed `MessageRouter` to `RouteMgr`.
- Remove dependency on ConstGroup.

### Fixed
- Integration of `BootstrapMgr`, `SQLDb` and `InstallMgr` modules.
- Set the `id` for the *Introduction* label on the `InitialSetupPane`.
- `pages/Schema.md`:
  - Corrected *Internal P2Pool* section header name.

### Removed
- `DbCache` module.
- `Job` module. It has been replaced by the `TUILogMsg` class.
- `TUILogMsg` module. It has replaced by `OpsDb:add_tui_log_line()`.

---

## [0.48.1] - 2025-10-17

### Added
- `SQLMgr:insert_one()` method.
  - Added `__dict__` methods to `Db4E`, `MoneroD`, `MoneroDRemote`, `P2Pool`, `P2PoolRemote` and `XMRig` classes to support the new `insert_one()` method.
- `SQLMgr:update_one()` method.
- `BootstrapMgr` module.
  - Added `tomli_w` module to support writing the `$HOME/.db4e` bootstrap file.
  - Updated the `pyproject.toml` and `poetry.lock` file.
- `InstallMgr` changes to support the `SQLMgr`.


### Fixed
- Field definitions in the `pages/Schema` page.
  - Added `ip_addr` to the `monerod` table.
  - Removed `enabled` from the `remote_p2pool` table. 
  - Added `instance` to the `remote_xmrig` table.

---

## [0.48.0] - 2025-10-17

### Added
- Additional constants to `DForm` to support code cleanup.
- New `HashratePlot` widget:
  - Modified `DSelect` constants file
- New `SQLMgr` to interface with *SQLite3* database.
  - Created detailed schema specification `/pages/Schema.md`
  - Created *constructor*, `init_db()`.
- Additional modules (`fastapi`, `uvicorn`, `pydantic`, `httpx` and `pytet-asyncio`) to support the new client/server architecture.

### Refactor
- Code cleanup to `ChainBlocksFoundPane`, `ChainHashratesPane`, `ChainPane`, `Db4EPane`, `InitialSetupPane`, `LogViewPane`, `MoneroDPane`, `MoneroDRemotePane`, `P2PoolHashratesPane`, `P2PoolPane`, `P2PoolRemotePane`, `PaymentsPane`, `RuntimePane`, `StartStopLogPane`, `TUILogPane`, `XMRigHashratesPane`, `XMRigPane`, `XMRigRemotePane` and `Db4EPlot` widget module files.

### Changed
- Set `allow_blank=False` on the `P2PoolSharesFoundPane`, `XMRigSharesFoundPane`, `ChainHashratesPane`, `InitialSetupPane` panes.
- Replaced `Db4ePlot` with new `HashratePlot`:
  - Updated `P2PoolHashratesPane`, `XMRigHashratesPane` and `ChainHashratesPane` panes.
- Replaced `Db4ePlot` with `SharesFound` plot in `XMRigSharesFoundPane`.
- Updated [website](https://db4e.osoyalce.com) and `README`.

### Fixed
- Case where there is no data in the `Db4ePlot` widget.
- Fixed incorrect time value in *hashrate plot* time range selection; added a `ONE_WEEK_HOURS` constant to the `DSelect` file.

---

## [0.47.2] - 2025-10-15 

### Fixed
- Git tag issue

---

## [0.47.0] - 2025-10-15 

### Added
- Created a new `XMRigRemoteHashratePane`
  - Took the *hashrate* plot out of the `XMRigRemotePane`
  - Added the new pant to the `DPane` constants file.
  - Added a new route to the `MessageRouter`
  - Added a new pane to the `PaneCatalogue`
- Created a new `XMRigSharesFoundPane`
  - Added `shares_found()` get/set methods to the `XMRig` and `XMRigRemote` classes.
  - Added new constants to the `DForm` and `DLabel` constants file.
  - Added a new route to the `MessageRouter`
  - Added a new pane to the `PaneCatalogue`
  - Created a `SharesFoundPlot` widget
- Support for *SQLite3* in the `pyproject.toml` file:
  - Planned migration from *Mongo* to *SQLite3*
  - Stubbed out a `SQLiteMgr` module.

### Fixed
- Fixed the path in the comments banner for the `P2PoolHashratePane`

### Changed
- Refactor of *P2Pool Shares Found*:
  - Refactored `P2PoolSharesFound` pane code.
  - Replaced the `Db4ePlot` widget with the new `SharesFoundPlot` widget.
  
---

## [0.46.0] - 2025-10-07

### Added 
- Additional website screenshots
- Added a XMR payment plot
  - Added *Payments* button.
  - Added values to `DButton`, `DLabel` and `DField` constants files.

### Changed
- Renamed `HashratePlot` widget to `Db4EWidget` since it's used to plot hashrates, shares found and XMR Payment data.
  - Updated `ChainHashratesPane`, `P2PoolSharesFoundPane`, `XMRigHashratesPane` and `XMRigRemotePane`

### Fixed
- In `DeplMgr:get_deployment()`, check that a *P2Pool* instance is local before trying to reference it's parent.
- In `DeplClient:add_deployument()`, do not add a new deployment if there are missing fields.
- Create *backup* and *logrotate* directories correctly in `InstallMgr`
- Remove references to *logging collection* in `DbMgr`
- Created `Helper:sudo_del_file()` function to delete *logrotate* configuration files when a *P2Pool* or *XMRig* deployment is deleted.
- Ensure that the *P2Pool* socket is created when a *P2Pool* instance is started.
- Corrected duplicate `OpsMgr` in `images/App-Releationships.png`

---

## [0.45.1] - 2025-10-07

### Fixed
- Git tagging issue

---

## [0.45.0] - 2025-10-07 

### Added
- Added *Start/Stop* to `DLabel`
- Bar chart for *Shares Found*
- Per miner stacked bar chart for *Shares Found*
- `Textual-Plot` based chart for *Shares Found*
  - Added `MiningDb:get_shares_found()` and `MiningETL:get_shares_found()` methods.
  - Added routes to the `MessageRouter`
  - Added `OpsMgr:get_shares_found()` method.
  - Added `P2PoolSharesFoundPane` to display a bar chart of the *Shares Found* data.

### Changed
- Moved `logrotate` directory (logrotate config files) from `vendor_dir/db4e to` `vendor_dir`
- Renamed *Runtime* to *Start/Stop* log in `DPane`, `PaneCatalogue`, `MessageRouter`, `OpsMgr` and `NavPane`
- Renamed *Uptime* to *Runtime* log in `DPane`, `Db4EPane`, `PaneCatalogue`, `MessageRouter` and `OpsMgr` 

### Removed
- Bar chart for *Shares Found*; `textual-plotext` doesn't support changing the time range
- Per miner stacked bar chart for *Blocks Found*: 
  - `textual-plotext` doesn't support changing the time range
  - `textual-plotext` provides too few colors, they get reused making the plot useless

---

## [0.44.1] - 2025-10-05

### Changed
- Minor website edits.

### Fixed
- Broken image on the website.

---

## [0.44.0] - 2025-10-05

### Added
- Added a new *Block Found* bar chart visualization for the *Main Chain*, "Mini SideChain" and "Nano SideChain"
  - Added *Blocks Found* constants to the `DButton`, `DField`, `DLabel`, `DMethod` and `DPange` constants files.
  - Added styling for the *Blocks Found* button to the `Db4E.tcss` file.
  - Added a new `ChainBlocksFoundPane` to display a bar chart of the *Blocks Found* data.
  - Added routes to the `MessageRouter`
  - Added `MiningETL:get_blocks_found()` and `MiningDb:get_blocks_found()` methods.
  - Added code to `ChainPane` to support the new *Blocks Found* button.
  - Added screenshot of the *Blocks Found&* bar chart visualzation to the *Db4E website*.

### Changed
- Modified the `MiningDb` for backend schema for the *Blocks Found* data.

### Fixed
- Bug in the `Db4EServer` that checked for a `parent()` function on *Remote P2Pool intances*

---

## [0.43.0] - 2025-10-05

### Added
- Daily backup of compressed DB4E Mongo collections
  - Added rotation of Mongo backup files.
- Screenshots the to https://db4e.osoyalce.com/ project site.

### Fixed
- Added a `Db4EServer:chown_logrotate_files()` function to set the permissions on the *logrotate* configuration files.
- Removed `daily` from logrotate files; *Db4E* rotates log files based on size.

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
