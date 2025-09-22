"""
db4e/Panes/P2PoolInternal.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from dataclasses import dataclass
from typing import Any

from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.message import Message
from textual.widgets import (Label, Button)
from textual.reactive import var
from textual import on, work

from db4e.Modules.InternalP2Pool import InternalP2Pool

from db4e.Widgets.HashratePlot import HashratePlot

from db4e.Messages.Db4eMsg import Db4eMsg

from db4e.Constants.DButton import DButton
from db4e.Constants.DJob import DJob
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DModule import DModule
from db4e.Constants.DElem import DElem
from db4e.Constants.DForm import DForm

class P2PoolInternalPane(Container):


    instance_label = Label("", id="instance_label",classes=DForm.STATIC)
    config_file_label = Label("", id="config_label", classes=DForm.STATIC)
    stratum_port_label = Label("", id="stratum_port_label", classes=DForm.STATIC)
    p2p_port_label = Label("", id="p2p_port_label", classes=DForm.STATIC)
    view_log_button = Button(label=DLabel.VIEW_LOG, id=DButton.VIEW_LOG)
    p2pool = None

    @dataclass
    class HashrateData(Message):
        history: dict[str, Any]


    def compose(self):
        # Internal P2Pool daemon deployment form
        INTRO = f"View information about the [cyan]{DLabel.P2POOL_INTERNAL}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        self.instance_label),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=DForm.FORM_LABEL),
                        self.stratum_port_label),
                    Horizontal(
                        Label(DLabel.P2P_PORT, classes=DForm.FORM_LABEL),
                        self.p2p_port_label),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL),
                        self.config_file_label),
                    classes=DForm.FORM_4, id="form_field"),

                Vertical(
                    HashratePlot("Hashrate", id="hashrate_plot")
                ),

                Vertical(
                    self.view_log_button
                )),
                classes=DForm.PANE_BOX)
        

    def set_data(self, p2pool: InternalP2Pool):
        self.p2pool = p2pool
        self.instance_label.update(p2pool.instance())
        self.config_file_label.update(p2pool.config_file())
        self.stratum_port_label.update(str(p2pool.stratum_port()))
        self.p2p_port_label.update(str(p2pool.p2p_port()))
        hashrate_plot = self.query_one("#hashrate_plot")
        print(p2pool.hashrates())
        hashrate_plot.update(p2pool.hashrates())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        form_data = {
            DField.ELEMENT_TYPE: DElem.INT_P2POOL,
            DField.TO_MODULE: DModule.OPS_MGR,
            DField.TO_METHOD: DMethod.LOG_VIEWER,
            DField.INSTANCE: self.p2pool.instance()
        }
        self.app.post_message(Db4eMsg(self, form_data=form_data))