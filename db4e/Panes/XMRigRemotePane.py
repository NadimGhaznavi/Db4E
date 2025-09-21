"""
db4e/Panes/XMRigRemotePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Label, Input, Button, RadioSet, RadioButton)

from db4e.Modules.Helper import gen_results_table
from db4e.Modules.XMRigRemote import XMRigRemote
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.DButton import DButton
from db4e.Constants.DJob import DJob
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DModule import DModule
from db4e.Constants.DElem import DElem
from db4e.Constants.DForm import DForm


class XMRigRemotePane(Container):


    instance_label = Label("", id="instance_label",classes=DForm.STATIC)
    ip_addr_label = Label("", id="ip_addr_label", classes=DForm.STATIC)
    hashrate_label = Label("", id="hashrate_label", classes=DForm.STATIC)
    uptime_label = Label("", id="uptime_label", classes=DForm.STATIC)
    xmrig_remote = None


    def compose(self):
        # Remote P2Pool daemon deployment form
        INTRO = f"View information about the [cyan]{DLabel.XMRIG_REMOTE}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        self.instance_label),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=DForm.FORM_LABEL),
                        self.ip_addr_label),
                    Horizontal(
                        Label(DLabel.HASHRATE, classes=DForm.FORM_LABEL),
                        self.hashrate_label),
                    Horizontal(
                        Label(DLabel.UPTIME, classes=DForm.FORM_LABEL),
                        self.uptime_label),
                    classes=DForm.FORM_4, id="form_field"),
                
            classes=DForm.PANE_BOX))

    def set_data(self, xmrig: XMRigRemote):
        #print(f"XMRig:set_data(): {xmrig}")
        self.xmrig = xmrig
        self.instance_label.update(xmrig.instance())
        self.ip_addr_label.update(xmrig.ip_addr())
        self.hashrate_label.update(str(xmrig.hashrate()) + " H/s")
        self.uptime_label.update(xmrig.uptime())
        