"""
db4e/App.py

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


from db4e.Widgets.TopBar import TopBar
from db4e.Widgets.NavPane import NavPane
from db4e.Widgets.Clock import Clock

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Messages.UpdateTopBar import UpdateTopBar

from db4e.Modules.DbCache import DbCache
from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.DeplClient import DeplClient
from db4e.Modules.HealthCache import HealthCache
from db4e.Modules.InstallMgr import InstallMgr
from db4e.Modules.MessageRouter import MessageRouter
from db4e.Modules.MiningDb import MiningDb
from db4e.Modules.OpsDb import OpsDb, OpsETL
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue

from db4e.Constants.DDef import DDef
from db4e.Constants.DField import DField

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
    panel="#000000",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)

class Db4EApp(App):
    TITLE = DDef.APP_TITLE
    CSS_PATH = DDef.CSS_PATH
    REFRESH_TIME = 2

    def __init__(self):
        # App Class Relationships diagram: 
        # https://drive.google.com/file/d/1-a46C_5FcseLEv-8aOY-FVzGjycesr8q/view?usp=drive_link
        super().__init__()
        db = DbMgr()
        ops_db = OpsDb(db=db)
        ops_etl = OpsETL(ops_db=ops_db)
        mining_db = MiningDb(db=db, ops_etl=ops_etl)
        db_cache = DbCache(db=db, mining_db=mining_db)
        depl_client = DeplClient(db=db, db_cache=db_cache)
        health_cache = HealthCache(depl_client=depl_client)
        ops_mgr = OpsMgr(
            depl_client=depl_client, health_cache=health_cache, db_cache=db_cache, 
            mining_db=mining_db, ops_etl=ops_etl)
        install_mgr = InstallMgr(db=db, db_cache=db_cache)

        self.pane_mgr = PaneMgr(catalogue=PaneCatalogue())
        self.nav_pane = NavPane(health_cache=health_cache, ops_mgr=ops_mgr)
        self.msg_router = MessageRouter(
            depl_client=depl_client, install_mgr=install_mgr, pane_mgr=self.pane_mgr,
            ops_mgr=ops_mgr)



    def compose(self):
        self.topbar = TopBar(app_version=__version__)
        yield self.topbar
        yield Vertical(
            self.nav_pane,
            Clock()
        )
        yield self.pane_mgr


    def on_mount(self) -> None:
        # Register the theme
        self.register_theme(db4e_theme)  

        # Set the app's theme
        self.theme = "db4e"  

    ### Message handling happens here...#31b8e6;

    # Exit the app
    def on_quit(self) -> None:
        self.exit()
    
    # Every form sends the form data here
    @work(exclusive=True)
    async def on_db4e_msg(self, message: Db4eMsg) -> None:
        #print(f"Db4EApp:on_db4e_msg(): form_data: {message.form_data}")
        data, pane = self.msg_router.dispatch(
            message.form_data[DField.TO_MODULE],
            message.form_data[DField.TO_METHOD],
            message.form_data
        )
        #print(f"Db4EApp:on_db4e_msg(): pane: {pane}, data: {data}")
        self.pane_mgr.set_pane(name=pane, data=data)

    # Handle requests to refresh the NavPane
    @work(exclusive=True)
    async def on_refresh_nav_pane(self, message: RefreshNavPane) -> None:
        self.nav_pane.refresh_nav_pane()


    # The individual Detail panes use this to update the TopBar
    def on_update_top_bar(self, message: UpdateTopBar) -> None:
        self.topbar.set_state(title=message.title, sub_title=message.sub_title )

    # Catchall 
    def _handle_exception(self, error: Exception) -> None:
        self.bell()
        self.exit(message=Traceback(show_locals=True, width=None, locals_max_length=5))

def main():
    # Set environment variables for better color support
    os.environ[DField.TERM_ENVIRON] = DDef.TERM
    os.environ[DField.COLORTERM_ENVIRON] = DDef.COLORTERM

    app = Db4EApp()
    app.run()

if __name__ == "__main__":
    main()