"""
db4e/Panes/P2PoolRemotePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Button, Input

from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.Helper import gen_results_table
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DModule import DModule
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DButton import DButton
from db4e.Constants.DForm import DForm


class P2PoolRemotePane(Container):

    p2pool: P2PoolRemote = None

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.INSTANCE_INPUT,
                            restrict="[a-zA-Z0-9_\-]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                        Label("", classes=DForm.STATIC, id=DForm.INSTANCE_LABEL),
                    ),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.IP_ADDR_INPUT,
                            restrict="[a-z0-9._\-]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.STRATUM_PORT_INPUT,
                            restrict="[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    id=DForm.FORM_BOX,
                    classes=DForm.FORM_3,
                ),
                Vertical(
                    Label("", id=DForm.HEALTH_LABEL),
                    id=DForm.HEALTH_BOX,
                    classes=DForm.HEALTH_BOX,
                ),
                Horizontal(
                    Button(DLabel.NEW, id=DButton.NEW),
                    Button(DLabel.UPDATE, id=DButton.UPDATE),
                    Button(DLabel.DELETE, id=DButton.DELETE),
                    classes=DForm.BUTTON_ROW,
                ),
                classes=DForm.PANE_BOX,
            )
        )

    def on_mount(self):
        self.query_one(f"#{DForm.FORM_BOX}", Vertical).border_subtitle = DLabel.CONFIG
        self.query_one(f"#{DForm.HEALTH_BOX}", Vertical).border_subtitle = DLabel.STATUS

    def set_data(self, p2pool: P2PoolRemote):
        self.p2pool = p2pool

        self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value = p2pool.instance()
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(p2pool.instance())
        self.query_one(f"#{DForm.IP_ADDR_INPUT}", Input).value = p2pool.ip_addr()
        self.query_one(f"#{DForm.STRATUM_PORT_INPUT}", Input).value = str(
            p2pool.stratum_port()
        )
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(p2pool.pop_msgs())
        )

        # Configure intro text & button visibility
        if p2pool.instance():
            intro_text = (
                f"Configure the settings for the [cyan]{p2pool.instance()} {DLabel.P2POOL_REMOTE}[/] deployment. "
                f"[b]NOTE[/]: Clicking the [cyan]enable/disable[/] button will not start/stop the software on the remote instance."
            )
            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)
        else:
            intro_text = (
                f"Configure the deployment settings for a new [cyan]{DLabel.P2POOL_REMOTE}[/] deployment here. "
                f"[b]NOTE[/]: This will [b]not[/] install the [cyan]{DLabel.P2POOL_REMOTE}[/] software on a remote machine. "
                f"This record is used to support the deployment of local [cyan]{DLabel.XMRIG}[/] deployments."
            )
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.query_one(f"#{DForm.INTRO}", Label).update(intro_text)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        # Update p2pool object with current input values
        self.p2pool.instance(self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value)
        self.p2pool.ip_addr(self.query_one(f"#{DForm.IP_ADDR_INPUT}", Input).value)
        self.p2pool.stratum_port(
            self.query_one(f"#{DForm.STRATUM_PORT_INPUT}", Input).value
        )

        # Map button to action
        button_map = {
            DButton.NEW: (DModule.OPS_MGR, DMethod.ADD_DEPLOYMENT),
            DButton.UPDATE: (DModule.DEPLOYMENT_CLIENT, DMethod.UPDATE_DEPLOYMENT),
            DButton.DELETE: (DModule.DEPLOYMENT_CLIENT, DMethod.DELETE_DEPLOYMENT),
        }

        if button_id not in button_map:
            raise ValueError(f"No handler for button {button_id}")

        module, method = button_map[button_id]
        form_data = {
            DField.TO_MODULE: module,
            DField.TO_METHOD: method,
            DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
            DField.ELEMENT: self.p2pool,
        }

        self.app.post_message(Db4eMsg(self, form_data=form_data))
