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
from textual.widgets import Label, Button

from db4e.Modules.XMRigRemote import XMRigRemote
from db4e.Messages.Db4eMsg import Db4eMsg

from db4e.Modules.Helper import minutes_to_uptime

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DForm import DForm
from db4e.Constants.DButton import DButton
from db4e.Constants.DElem import DElem
from db4e.Constants.DModule import DModule
from db4e.Constants.DMethod import DMethod




class XMRigRemotePane(Container):

    instance_label = Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC)
    ip_addr_label = Label("", id=DForm.IP_ADDR_LABEL, classes=DForm.STATIC)
    hashrate_label = Label("", id=DForm.HASHRATE_LABEL, classes=DForm.STATIC)
    uptime_label = Label("", id=DForm.UPTIME_LABEL, classes=DForm.STATIC)
    hashrate_button = Button(label=DLabel.HASHRATE, id=DButton.HASHRATE)
    shares_found_button = Button(label=DLabel.SHARES_FOUND, id=DButton.SHARES_FOUND)
    xmrig = None


    def compose(self):
        # Remote P2Pool daemon deployment form
        INTRO = f"View information about the [cyan]{DLabel.XMRIG_REMOTE}[/] deployment."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_20),
                        self.instance_label),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=DForm.FORM_LABEL_20),
                        self.ip_addr_label),
                    Horizontal(
                        Label(DLabel.HASHRATE, classes=DForm.FORM_LABEL_20),
                        self.hashrate_label),
                    Horizontal(
                        Label(DLabel.UPTIME, classes=DForm.FORM_LABEL_20),
                        self.uptime_label),
                    classes=DForm.FORM_4, id=DForm.FORM_FIELD),

                Vertical(
                    Horizontal(
                        self.hashrate_button,
                        self.shares_found_button,
                        classes=DForm.BUTTON_ROW))),

                classes=DForm.PANE_BOX)


    def set_data(self, xmrig: XMRigRemote):
        self.xmrig = xmrig
        self.instance_label.update(xmrig.instance())
        self.ip_addr_label.update(xmrig.ip_addr())
        self.hashrate_label.update(str(xmrig.hashrate()) + " " + DLabel.H_PER_S)
        self.uptime_label.update(minutes_to_uptime(xmrig.uptime()))


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == DButton.HASHRATE:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.HASHRATES,
                DField.ELEMENT_TYPE: DElem.XMRIG_REMOTE,
                DField.ELEMENT: self.xmrig,
            }
        
        elif button_id == DButton.SHARES_FOUND:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.SHARES_FOUND,
                DField.ELEMENT_TYPE: DElem.XMRIG_REMOTE,
                DField.ELEMENT: self.xmrig,
            }

        self.app.post_message(Db4eMsg(self, form_data=form_data))
