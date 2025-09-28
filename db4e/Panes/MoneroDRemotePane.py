"""
db4e/Panes/MoneroDRemotePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Button, Input, Checkbox

from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.Helper import gen_results_table
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DModule import DModule
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DJob import DJob
from db4e.Constants.DButton import DButton
from db4e.Constants.DForm import DForm


class MoneroDRemotePane(Container):

    intro_label = Label("", classes=DForm.INTRO, id=DForm.INTRO)
    instance_label = Label("", id=DForm.INSTANCE_LABEL,classes=DForm.STATIC)
    instance_input = Input(
        compact=True, id=DForm.INSTANCE_INPUT, restrict=f"[a-zA-Z0-9_\-]*",
        classes=DForm.INPUT_30)
    ip_addr_input = Input(
        compact=True, id=DForm.IP_ADDR_INPUT, restrict=f"[a-z0-9._\-]*",
        classes=DForm.INPUT_30)
    rpc_bind_port_input = Input(
        compact=True, id=DForm.RPC_BIND_PORT_INPUT, restrict=f"[0-9]*",
        classes=DForm.INPUT_30)
    zmq_pub_port_input = Input(
        compact=True, id=DForm.ZMQ_PUB_PORT_INPUT, restrict=f"[0-9]*",
        classes=DForm.INPUT_30)
    health_msgs = Label()
    delete_button = Button(label=DLabel.DELETE, id=DButton.DELETE)
    new_button = Button(label=DLabel.NEW, id=DButton.NEW)
    update_button = Button(label=DLabel.UPDATE, id=DButton.UPDATE)


    def compose(self):
        # Remote Monero daemon deployment form
        yield Vertical(
            ScrollableContainer(
                self.intro_label,

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=DForm.FORM_LABEL),
                        self.ip_addr_input),
                    Horizontal(
                        Label(DLabel.RPC_BIND_PORT, classes=DForm.FORM_LABEL),
                        self.rpc_bind_port_input),
                    Horizontal(
                        Label(DLabel.ZMQ_PUB_PORT, classes=DForm.FORM_LABEL),
                        self.zmq_pub_port_input),
                    classes=DForm.FORM_4, id=DForm.FORM_BOX),

                Vertical(
                    self.health_msgs,
                    classes=DForm.HEALTH_BOX, id=DForm.HEALTH_BOX),

                Horizontal(
                    self.new_button,
                    self.update_button,
                    self.delete_button,
                    classes=DForm.BUTTON_ROW)),

            classes=DForm.PANE_BOX)

    def on_mount(self):
        form_box = self.query_one("#" + DForm.FORM_BOX, Vertical)
        form_box.border_subtitle = DLabel.CONFIG
        health_box = self.query_one("#" + DForm.HEALTH_BOX, Vertical)
        health_box.border_subtitle = DLabel.STATUS


    def set_data(self, monerod: MoneroDRemote):
        #(f"MonerodRemote:set_data(): rec: {rec}")
        self.instance_input.value = monerod.instance()
        self.instance_label.update(monerod.instance())
        self.ip_addr_input.value = monerod.ip_addr()
        self.rpc_bind_port_input.value = str(monerod.rpc_bind_port())
        self.zmq_pub_port_input.value = str(monerod.zmq_pub_port())
        self.health_msgs.update(gen_results_table(monerod.pop_msgs()))
        self.monerod = monerod
        # Set update button or new button visibility, using the .tcss definitions
        if monerod.instance():
            # This is an update operation
            INTRO = f"Configure the settings for the " \
            f"[cyan]{monerod.instance()} {DLabel.MONEROD_REMOTE}[/] deployment. " \
            f"[b]NOTE[/]: Clicking the [cyan]enable/disable[/] " \
            f"button will not start/stop the software on the remote instance. "

            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)

        else:
            INTRO = f"Configure the deployment settings for a new " \
            f"[cyan]{DLabel.MONEROD_REMOTE}[/] deployment here. [b]NOTE[/]: This will " \
            f"[b]not[/] install the [cyan]{DLabel.MONEROD_REMOTE}[/] software on a " \
            f"remote machine. This record is used to support the deployment of local " \
            f"[cyan]{DLabel.P2POOL}[/] deployments." 
            # This is a new operation
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)
        self.intro_label.update(INTRO)


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        self.monerod.instance(self.query_one("#" + DForm.INSTANCE_INPUT, Input).value)
        self.monerod.ip_addr(self.query_one("#" + DForm.IP_ADDR_INPUT, Input).value)
        self.monerod.rpc_bind_port(self.query_one("#" + DForm.RPC_BIND_PORT_INPUT, Input).value)
        self.monerod.zmq_pub_port(self.query_one("#" + DForm.ZMQ_PUB_PORT_INPUT, Input).value)


        if button_id == DButton.NEW:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                DField.ELEMENT: self.monerod,
            }                

        elif button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.UPDATE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DELETE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                DField.ELEMENT: self.monerod,
            }
        else:
            raise ValueError(f"No handler for {button_id}")
        self.app.post_message(Db4eMsg(self, form_data=form_data))
        #self.app.post_message(RefreshNavPane(self))