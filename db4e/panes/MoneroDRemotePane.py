# db4e/Panes/MoneroDRemotePane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Button, Input

from db4e.messages.Db4EMsg import Db4EMsg
from db4e.recs.monero.MoneroDRemote import MoneroDRemote
from db4e.util.Helper import gen_results_table
from db4e.constants.DField import DField
from db4e.constants.DElem import DElem
from db4e.constants.DModule import DModule
from db4e.constants.DMethod import DMethod
from db4e.constants.DLabel import DLabel
from db4e.constants.DButton import DButtonF, DButtonL
from db4e.constants.DForm import DForm


class MoneroDRemotePane(Container):
    """Textual pane for MoneroDRemotePane."""

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        # Remote Monero daemon deployment form
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        Input(
                            compact=True,
                            id=DForm.INSTANCE_INPUT,
                            restrict=f"[a-zA-Z0-9_\\-]*",
                            classes=DForm.INPUT_30,
                        ),
                        Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=DForm.FORM_LABEL),
                        Input(
                            compact=True,
                            id=DForm.IP_ADDR_INPUT,
                            restrict=f"[a-z0-9._\\-]*",
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.RPC_BIND_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            compact=True,
                            id=DForm.RPC_BIND_PORT_INPUT,
                            restrict=f"[0-9]*",
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.ZMQ_PUB_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            compact=True,
                            id=DForm.ZMQ_PUB_PORT_INPUT,
                            restrict=f"[0-9]*",
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    classes=DForm.FORM_4,
                    id=DForm.FORM_BOX,
                ),
                Vertical(
                    Label("", id=DForm.HEALTH_LABEL, classes=DForm.HEALTH_LABEL),
                    classes=DForm.HEALTH_BOX,
                    id=DForm.HEALTH_BOX,
                ),
                Horizontal(
                    Button(label=DButtonL.NEW, id=DButtonF.NEW),
                    Button(label=DButtonL.UPDATE, id=DButtonF.UPDATE),
                    Button(label=DButtonL.DELETE, id=DButtonF.DELETE),
                    classes=DForm.BUTTON_ROW,
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_mount(self):
        """Handle the mount lifecycle event.

        :return: None
        :rtype: None
        """
        form_box = self.query_one(f"#{DForm.FORM_BOX}", Vertical)
        form_box.border_subtitle = DLabel.CONFIG
        health_box = self.query_one(f"#{DForm.HEALTH_BOX}", Vertical)
        health_box.border_subtitle = DLabel.STATUS

    def set_data(self, monerod: MoneroDRemote):
        """Set the data for the pane.

        :param monerod: MoneroD deployment object.
        :type monerod: MoneroDRemote
        :return: None
        :rtype: None
        """
        if monerod.instance():
            self.add_class(DField.EDIT)
        self.monerod = monerod
        self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value = monerod.instance()
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(monerod.instance())
        self.query_one(f"#{DForm.IP_ADDR_INPUT}", Input).value = monerod.ip_addr()
        self.query_one(f"#{DForm.RPC_BIND_PORT_INPUT}", Input).value = str(
            monerod.rpc_bind_port()
        )
        self.query_one(f"#{DForm.ZMQ_PUB_PORT_INPUT}", Input).value = str(
            monerod.zmq_pub_port()
        )
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(monerod.pop_msgs())
        )

        # Configure intro text and CSS classes
        if monerod.instance():
            INTRO = (
                f"Configure the settings for the "
                f"[cyan]{monerod.instance()} {DLabel.MONEROD_REMOTE}[/] deployment. "
                f"[b]NOTE[/]: Clicking the [cyan]enable/disable[/] button will not "
                f"start/stop the software on the remote instance."
            )
            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)

        else:
            INTRO = (
                f"Configure the deployment settings for a new "
                f"[cyan]{DLabel.MONEROD_REMOTE}[/] deployment here. [b]NOTE[/]: This will "
                f"[b]not[/] install the [cyan]{DLabel.MONEROD_REMOTE}[/] software on a "
                f"remote machine. This record is used to support the deployment of "
                f"[cyan]local {DLabel.P2POOL}[/] deployments."
            )
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.query_one(f"#{DForm.INTRO}", Label).update(INTRO)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button pressed events.

        :param event: Event payload.
        :type event: Button.Pressed
        :return: None
        :rtype: None
        """

        button_id = event.button.id

        self.monerod.instance(self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value)
        self.monerod.ip_addr(self.query_one(f"#{DForm.IP_ADDR_INPUT}", Input).value)
        self.monerod.rpc_bind_port(
            self.query_one(f"#{DForm.RPC_BIND_PORT_INPUT}", Input).value
        )
        self.monerod.zmq_pub_port(
            self.query_one(f"#{DForm.ZMQ_PUB_PORT_INPUT}", Input).value
        )

        # Map button to action
        button_map = {
            DButtonF.NEW: (DModule.SYNC_CLIENT, DMethod.ADD_DEPLOYMENT),
            DButtonF.UPDATE: (DModule.SYNC_CLIENT, DMethod.UPDATE_DEPLOYMENT),
            DButtonF.DELETE: (DModule.SYNC_CLIENT, DMethod.DELETE_DEPLOYMENT),
        }

        if button_id not in button_map:
            raise ValueError(f"No handler for button {button_id}")

        module, method = button_map[button_id]

        form_data = {
            DField.TO_MODULE: module,
            DField.TO_METHOD: method,
            DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
            DField.ELEMENT: self.monerod,
        }

        self.remove_class(DField.EDIT)
        self.app.post_message(Db4EMsg(self, form_data=form_data))
