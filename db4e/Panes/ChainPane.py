"""
db4e/Panes/P2PoolInternalPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Label, Button

from db4e.Modules.Helper import gen_results_table
from db4e.Modules.InternalP2Pool import InternalP2Pool

from db4e.Messages.Db4eMsg import Db4eMsg

from db4e.Constants.DButton import DButton
from db4e.Constants.DJob import DJob
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DModule import DModule
from db4e.Constants.DElem import DElem
from db4e.Constants.DForm import DForm


class ChainPane(Container):

    p2pool = None

    def compose(self):
        # Internal P2Pool daemon analythics form
        INTRO = f"View information about the [cyan]{DLabel.P2POOL_INTERNAL}[/] deployment here."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.IN_PEERS, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.IN_PEERS_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.OUT_PEERS, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.OUT_PEERS_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.P2P_PORT, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.P2P_PORT_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.STRATUM_PORT_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.LOG_LEVEL, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.LOG_LEVEL_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.UPSTREAM_MONERO, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.PARENT_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.CONFIG_FILE_LABEL, classes=DForm.STATIC),
                    ),
                    id=DForm.FORM_BOX,
                    classes=DForm.FORM_8,
                ),
                Vertical(
                    Label(id=DForm.HEALTH_LABEL),
                    classes=DForm.HEALTH_BOX,
                    id=DForm.HEALTH_BOX,
                ),
                Vertical(
                    Horizontal(
                        Button(label=DLabel.BLOCKS_FOUND, id=DButton.BLOCKS_FOUND),
                        Button(label=DLabel.HASHRATE, id=DButton.HASHRATE),
                        Button(label=DLabel.VIEW_LOG, id=DButton.VIEW_LOG),
                        Button(label=DLabel.RESTART, id=DButton.RESTART),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_mount(self):
        self.query_one("#" + DForm.FORM_BOX, Vertical).border_subtitle = DLabel.CONFIG
        self.query_one("#" + DForm.HEALTH_BOX, Vertical).border_subtitle = DLabel.STATUS

    def set_data(self, p2pool: InternalP2Pool):
        self.p2pool = p2pool
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(p2pool.instance())
        self.query_one(f"#{DForm.CONFIG_FILE_LABEL}", Label).update(
            p2pool.config_file()
        )
        self.query_one(f"#{DForm.IN_PEERS_LABEL}", Label).update(str(p2pool.in_peers()))
        self.query_one(f"#{DForm.OUT_PEERS_LABEL}", Label).update(
            str(p2pool.out_peers())
        )
        self.query_one(f"#{DForm.P2P_PORT_LABEL}", Label).update(str(p2pool.p2p_port()))
        self.query_one(f"#{DForm.STRATUM_PORT_LABEL}", Label).update(
            str(p2pool.stratum_port())
        )
        self.query_one(f"#{DForm.LOG_LEVEL_LABEL}", Label).update(
            str(p2pool.log_level())
        )
        if p2pool.monerod:
            self.query_one(f"#{DForm.PARENT_LABEL}", Label).update(p2pool.parent())
        else:
            self.query_one(f"#{DForm.PARENT_LABEL}", Label).update(
                "Primary server not set"
            )

        # Health messages
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(p2pool.pop_msgs())
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == DButton.BLOCKS_FOUND:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.BLOCKS_FOUND,
                DField.ELEMENT_TYPE: DElem.INT_P2POOL,
                DField.ELEMENT: self.p2pool,
            }

        if button_id == DButton.HASHRATE:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.HASHRATES,
                DField.ELEMENT_TYPE: DElem.INT_P2POOL,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButton.RESTART:
            form_data = {
                DField.ELEMENT_TYPE: DElem.INT_P2POOL,
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.RESTART,
                DField.INSTANCE: self.p2pool.instance(),
            }

        elif button_id == DButton.VIEW_LOG:
            form_data = {
                DField.ELEMENT_TYPE: DElem.INT_P2POOL,
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.LOG_VIEWER,
                DField.INSTANCE: self.p2pool.instance(),
            }

        self.app.post_message(Db4eMsg(self, form_data=form_data))
