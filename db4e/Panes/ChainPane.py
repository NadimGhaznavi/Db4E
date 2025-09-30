"""
db4e/Panes/P2PoolInternalPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (Label, Button)

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

    instance_label = Label("", classes=DForm.STATIC)
    config_file_label = Label("", classes=DForm.STATIC)
    stratum_port_label = Label("", classes=DForm.STATIC)
    p2p_port_label = Label("", classes=DForm.STATIC)
    in_peers_label = Label("", classes=DForm.STATIC)
    out_peers_label = Label("", classes=DForm.STATIC)
    log_level_label = Label("", classes=DForm.STATIC)
    parent_label = Label("", classes=DForm.STATIC)

    analytics_button = Button(label=DLabel.ANALYTICS, id=DButton.ANALYTICS)
    hashrate_button = Button(label=DLabel.HASHRATE, id=DButton.HASHRATE)
    view_log_button = Button(label=DLabel.VIEW_LOG, id=DButton.VIEW_LOG)
    restart_button = Button(label=DLabel.RESTART, id=DButton.RESTART)

    health_msgs = Label()

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
                        self.instance_label),
                    Horizontal(
                        Label(DLabel.IN_PEERS, classes=DForm.FORM_LABEL),
                        self.in_peers_label),
                    Horizontal(
                        Label(DLabel.OUT_PEERS, classes=DForm.FORM_LABEL),
                        self.out_peers_label),
                    Horizontal(
                        Label(DLabel.P2P_PORT, classes=DForm.FORM_LABEL),
                        self.p2p_port_label),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=DForm.FORM_LABEL),
                        self.stratum_port_label),
                    Horizontal(
                        Label(DLabel.LOG_LEVEL, classes=DForm.FORM_LABEL),
                        self.log_level_label),
                    Horizontal(
                        Label(DLabel.UPSTREAM_MONERO, classes=DForm.FORM_LABEL),
                        self.parent_label),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL),
                        self.config_file_label),
                    id=DForm.FORM_BOX, classes=DForm.FORM_8),

                Vertical(
                    self.health_msgs,
                    classes=DForm.HEALTH_BOX, id=DForm.HEALTH_BOX
                ),

                Vertical(
                    Horizontal(
                        self.hashrate_button,
                        self.view_log_button,
                        self.restart_button,
                        classes=DForm.BUTTON_ROW))),
            classes=DForm.PANE_BOX)        


    def on_mount(self):
        form_box = self.query_one("#" + DForm.FORM_BOX, Vertical)
        form_box.border_subtitle = DLabel.CONFIG
        health_box = self.query_one("#" + DForm.HEALTH_BOX, Vertical)
        health_box.border_subtitle = DLabel.STATUS
        
        
    def set_data(self, p2pool: InternalP2Pool):
        self.p2pool = p2pool
        self.instance_label.update(p2pool.instance())
        self.config_file_label.update(p2pool.config_file())
        self.in_peers_label.update(str(p2pool.in_peers()))
        self.out_peers_label.update(str(p2pool.out_peers()))
        self.p2p_port_label.update(str(p2pool.p2p_port()))
        self.stratum_port_label.update(str(p2pool.stratum_port()))
        self.p2p_port_label.update(str(p2pool.p2p_port()))
        if p2pool.monerod:
            self.parent_label.update(str(p2pool.monerod.instance()))
        else:
            self.parent_label.update("Primary server disabled")
        self.log_level_label.update(str(p2pool.log_level()))


        # Health messages
        self.health_msgs.update(gen_results_table(p2pool.pop_msgs()))                    


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

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
                DField.INSTANCE: self.p2pool.instance()
            }

        elif button_id == DButton.VIEW_LOG:
            form_data = {
                DField.ELEMENT_TYPE: DElem.INT_P2POOL,
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.LOG_VIEWER,
                DField.INSTANCE: self.p2pool.instance()
            }

        self.app.post_message(Db4eMsg(self, form_data=form_data))

