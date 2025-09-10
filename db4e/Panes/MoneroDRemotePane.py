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
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import DField, DMod, DElem, Method
from db4e.Constants.Form import Form
from db4e.Constants.Labels import DLabel 
from db4e.Constants.Buttons import DButton
from db4e.Constants.Jobs import DJob


class MoneroDRemotePane(Container):

    instance_label = Label("", id="instance_label",classes=Form.STATIC.value)
    instance_input = Input(
        compact=True, id="instance_input", restrict=f"[a-zA-Z0-9_\-]*",
        classes=Form.INPUT_30.value)
    ip_addr_input = Input(
        compact=True, id="ip_addr_input", restrict=f"[a-z0-9._\-]*",
        classes=Form.INPUT_30.value)
    primary_server_checkbox = Checkbox(
        #PRIMARY_SERVER, compact=True, id="primary_server_checkbox")
        "", compact=True, id="primary_server_checkbox")
    rpc_bind_port_input = Input(
        compact=True, id="rpc_bind_port_input", restrict=f"[0-9]*",
        classes=Form.INPUT_30.value)
    zmq_pub_port_input = Input(
        compact=True, id="zmq_pub_port_input", restrict=f"[0-9]*",
        classes=Form.INPUT_30.value)
    health_msgs = Label()
    delete_button = Button(label=DLabel.DELETE.value, id=DButton.DELETE.value)
    new_button = Button(label=DLabel.NEW.value, id=DButton.NEW.value)
    update_button = Button(label=DLabel.UPDATE.value, id=DButton.UPDATE.value)


    def compose(self):
        # Remote Monero daemon deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{DLabel.MONEROD_REMOTE}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=Form.INTRO.value),

                Vertical(
                    Horizontal(
                        Label(DLabel.PRIMARY_SERVER, classes=Form.FORM_LABEL.value),
                        self.primary_server_checkbox),
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=Form.FORM_LABEL.value),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=Form.FORM_LABEL.value),
                        self.ip_addr_input),
                    Horizontal(
                        Label(DLabel.RPC_BIND_PORT, classes=Form.FORM_LABEL.value),
                        self.rpc_bind_port_input),
                    Horizontal(
                        Label(DLabel.ZMQ_PUB_PORT, classes=Form.FORM_LABEL.value),
                        self.zmq_pub_port_input),
                    classes=Form.FORM_5.value),

                Vertical(
                    self.health_msgs,
                    classes=Form.HEALTH_BOX.value),

                Horizontal(
                    self.new_button,
                    self.update_button,
                    self.delete_button,
                    classes=Form.BUTTON_ROW.value)),

            classes=Form.PANE_BOX.value)


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
            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)

        else:
            # This is a new operation
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)
        

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        self.monerod.instance(self.query_one("#instance_input", Input).value)
        self.monerod.ip_addr(self.query_one("#ip_addr_input", Input).value)
        self.monerod.rpc_bind_port(self.query_one("#rpc_bind_port_input", Input).value)
        self.monerod.zmq_pub_port(self.query_one("#zmq_pub_port_input", Input).value)
        self.monerod.primary_server(self.query_one("#primary_server_checkbox", Checkbox).value)


        if button_id == DButton.NEW:
            form_data = {
                DField.TO_MODULE: DMod.OPS_MGR,
                DField.TO_METHOD: Method.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                DField.ELEMENT: self.monerod,
            }                

        elif button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.UPDATE,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.DELETE,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                DField.ELEMENT: self.monerod,
            }
        else:
            raise ValueError(f"No handler for {button_id}")
        self.app.post_message(Db4eMsg(self, form_data=form_data))
        #self.app.post_message(RefreshNavPane(self))