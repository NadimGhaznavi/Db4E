"""
db4e/Db4EClient.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

import os
import time
from importlib import metadata
from textual.app import App
from textual.containers import Vertical
from textual import work
from rich.traceback import Traceback

try:
    __package_name__ = metadata.metadata(__package__ or __name__)["Name"]
    __version__ = metadata.version(__package__ or __name__)
except Exception:
    __package_name__ = "Db4E"
    __version__ = "N/A"


from db4e.widgets.TopBar import TopBar
from db4e.widgets.NavPane import NavPane
from db4e.widgets.Clock import Clock

from db4e.messages.Db4EMsg import Db4EMsg
from db4e.messages.RefreshNavPane import RefreshNavPane
from db4e.messages.UpdateTopBar import UpdateTopBar

from db4e.mgr.InstallMgr import InstallMgr
from db4e.mgr.RouteMgr import RouteMgr
from db4e.mgr.PaneMgr import PaneMgr
from db4e.mgr.BootstrapMgr import BootstrapMgr

from db4e.sync.SyncClient import SyncClient

from db4e.db.SQLDb import SQLDb
from db4e.db.DeplDb import DeplDb
from db4e.db.MiningDb import MiningDb
from db4e.db.OpsDb import OpsDb
from db4e.db.OpsETL import OpsETL
from db4e.db.HealthDb import HealthDb

from db4e.util.PaneCatalogue import PaneCatalogue

from db4e.constants.DDef import DDef
from db4e.constants.DField import DField
from db4e.constants.DPane import DPane
from db4e.constants.DDir import DDir

from textual.theme import Theme

db4e_theme = Theme(
    name="db4e",
    primary="#88C0D0",
    secondary="#1f6a83ff",
    accent="#B48EAD",
    foreground="#31b8e6",
    background="black",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="black",
    panel="#202020",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)


class Db4EClient(App):
    TITLE = DDef.APP_TITLE
    CSS_PATH = DDef.CSS_PATH
    REFRESH_TIME = 2

    def __init__(self):
        # App Class Relationships diagram:
        # https://drive.google.com/file/d/1-a46C_5FcseLEv-8aOY-FVzGjycesr8q/view?usp=drive_link
        super().__init__()
        self.bs_mgr = BootstrapMgr()
        self.sql_db = SQLDb(db_type=DField.CLIENT, bs_mgr=self.bs_mgr)
        self.ops_db = OpsDb(sql_db=self.sql_db)
        self.ops_etl = OpsETL(ops_db=self.ops_db)
        self.depl_db = DeplDb(sql_db=self.sql_db)
        self.mining_db = MiningDb(sql_db=self.sql_db)
        self.health_db = HealthDb(sql_db=self.sql_db)
        install_mgr = InstallMgr(bs_mgr=self.bs_mgr)
        self.pane_mgr = PaneMgr(catalogue=PaneCatalogue())
        self.nav_pane = NavPane(depl_db=self.depl_db)
        self.sync_client = SyncClient(
            sql_db=self.sql_db,
            ops_db=self.ops_db,
            depl_db=self.depl_db,
            bs_mgr=self.bs_mgr,
            server_url=f"http://{DDef.ANY_IP}:{DDef.API_PORT}",
        )
        self.msg_router = RouteMgr(
            depl_db=self.depl_db,
            ops_db=self.ops_db,
            install_mgr=install_mgr,
            pane_mgr=self.pane_mgr,
            sync_client=self.sync_client,
        )

    def compose(self):
        self.topbar = TopBar(app_version=__version__)
        yield self.topbar
        yield Vertical(self.nav_pane, Clock())
        yield self.pane_mgr

    async def on_mount(self) -> None:
        # Register the theme
        self.register_theme(db4e_theme)

        # Set the app's theme
        self.theme = "db4e"

        # Start background sync
        await self.sync_client.start()

    ### Message handling happens here...#31b8e6;

    # Exit the app
    async def on_quit(self) -> None:
        await self.sync_client.stop()
        self.exit()

    # Every form sends the form data here
    @work(exclusive=True)
    async def on_db4emsg(self, message: Db4EMsg) -> None:
        # print(f"Db4EApp:on_db4e_msg(): form_data: {message.form_data}")
        data, pane = await self.msg_router.dispatch(
            message.form_data[DField.TO_MODULE],
            message.form_data[DField.TO_METHOD],
            message.form_data,
        )
        # The Db4E database is within the deployment directory that's only defined
        # after a successful install. The results of the "InitialInstall" are put
        # into the tui_log_line table and the TUI Log Pane is displayed. We
        # intercept that call and initialize the client database when the
        # "InitialInstall" is successful.
        if (
            pane == DPane.TUI_LOG
            and type(data) == list
            and len(data) > 0
            and data[-1] == DField.INSTALL_SUCCESSFUL
        ):
            self.sql_db.initialize(self.bs_mgr.get_dir(DDir.DB))
            self.ops_db.initialize()
            self.depl_db.initialize()
            self.mining_db.initialize()
            self.health_db.initialize()
            self.pane_mgr.set_pane(name=pane, data=data[:-1])
        else:
            self.pane_mgr.set_pane(name=pane, data=data)

    # Handle requests to refresh the NavPane
    @work(exclusive=True)
    async def on_refresh_nav_pane(self, message: RefreshNavPane) -> None:
        self.nav_pane.refresh_nav_pane()

    # The individual Detail panes use this to update the TopBar
    def on_update_top_bar(self, message: UpdateTopBar) -> None:
        self.topbar.set_state(title=message.title, sub_title=message.sub_title)

    # Catchall
    def _handle_exception(self, error: Exception) -> None:
        self.bell()
        self.exit(message=Traceback(show_locals=True, width=None, locals_max_length=5))


def main():
    # Set environment variables for better color support
    os.environ[DField.TERM_ENVIRON] = DDef.TERM
    os.environ[DField.COLORTERM_ENVIRON] = DDef.COLORTERM

    app = Db4EClient()
    app.run()


if __name__ == "__main__":
    main()
