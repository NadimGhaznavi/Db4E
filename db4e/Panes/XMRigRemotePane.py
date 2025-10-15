"""
db4e/Panes/XMRigRemotePane.py

Database 4 Everything
Author: Nadim-Daniel Ghaznavi
Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
GitHub: https://github.com/NadimGhaznavi/db4e
License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
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

    xmrig: XMRigRemote | None = None

    def compose(self):
        intro = f"View information about the [cyan]{DLabel.XMRIG_REMOTE}[/] deployment."
        yield Vertical(
            ScrollableContainer(
                Label(intro, classes=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_20),
                        Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=DForm.FORM_LABEL_20),
                        Label("", id=DForm.IP_ADDR_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.HASHRATE, classes=DForm.FORM_LABEL_20),
                        Label("", id=DForm.HASHRATE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.UPTIME, classes=DForm.FORM_LABEL_20),
                        Label("", id=DForm.UPTIME_LABEL, classes=DForm.STATIC),
                    ),
                    classes=DForm.FORM_4,
                    id=DForm.FORM_FIELD,
                ),
                Vertical(
                    Horizontal(
                        Button(label=DLabel.HASHRATE, id=DButton.HASHRATE),
                        Button(label=DLabel.SHARES_FOUND, id=DButton.SHARES_FOUND),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def set_data(self, xmrig: XMRigRemote):
        self.xmrig = xmrig
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(xmrig.instance())
        self.query_one(f"#{DForm.IP_ADDR_LABEL}", Label).update(xmrig.ip_addr())
        self.query_one(f"#{DForm.HASHRATE_LABEL}", Label).update(
            f"{xmrig.hashrate()} {DLabel.H_PER_S}"
        )
        self.query_one(f"#{DForm.UPTIME_LABEL}", Label).update(
            minutes_to_uptime(xmrig.uptime())
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if not self.xmrig:
            return

        button_id = event.button.id
        method_map = {
            DButton.HASHRATE: DMethod.HASHRATES,
            DButton.SHARES_FOUND: DMethod.SHARES_FOUND,
        }

        if button_id in method_map:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: method_map[button_id],
                DField.ELEMENT_TYPE: DElem.XMRIG_REMOTE,
                DField.ELEMENT: self.xmrig,
            }
            self.app.post_message(Db4eMsg(self, form_data=form_data))
