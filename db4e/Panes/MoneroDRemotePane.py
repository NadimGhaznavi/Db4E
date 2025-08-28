"""
db4e/Panes/MoneroDRemotePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Button, Input

from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.Helper import gen_results_table
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, ELEMENT_TYPE_FIELD,
    FORM_4_FIELD, FORM_INPUT_30_FIELD, FORM_INTRO_FIELD, FORM_LABEL_FIELD,
    MONEROD_REMOTE_FIELD, HEALTH_BOX_FIELD, OPS_MGR_FIELD, 
    PANE_BOX_FIELD, ELEMENT_FIELD, INSTANCE_FIELD,
    TO_METHOD_FIELD, TO_MODULE_FIELD, 
    NEW_FIELD)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, IP_ADDR_LABEL, MONEROD_REMOTE_LABEL,
    RPC_BIND_PORT_LABEL, ZMQ_PUB_PORT_LABEL)
from db4e.Constants.Buttons import (
    BUTTON_ROW_FIELD, DELETE_BUTTON_FIELD, NEW_BUTTON_FIELD, UPDATE_BUTTON_FIELD,
    DELETE_LABEL, UPDATE_LABEL, NEW_LABEL)
from db4e.Constants.Jobs import (
    JOB_QUEUE_FIELD, POST_JOB_FIELD, OP_FIELD, DELETE_FIELD, UPDATE_FIELD)


class MoneroDRemotePane(Container):

    instance_input = Input(
        compact=True, id="instance_input", restrict=f"[a-zA-Z0-9_\-]*",
        classes=FORM_INPUT_30_FIELD)
    ip_addr_input = Input(
        compact=True, id="ip_addr_input", restrict=f"[a-z0-9._\-]*",
        classes=FORM_INPUT_30_FIELD)
    rpc_bind_port_input = Input(
        compact=True, id="rpc_bind_port_input", restrict=f"[0-9]*",
        classes=FORM_INPUT_30_FIELD)
    zmq_pub_port_input = Input(
        compact=True, id="zmq_pub_port_input", restrict=f"[0-9]*",
        classes=FORM_INPUT_30_FIELD)
    health_msgs = Label()
    delete_button = Button(label=DELETE_LABEL, id=DELETE_BUTTON_FIELD)
    new_button = Button(label=NEW_LABEL, id=NEW_BUTTON_FIELD)
    update_button = Button(label=UPDATE_LABEL, id=UPDATE_BUTTON_FIELD)


    def compose(self):
        # Remote Monero daemon deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{MONEROD_REMOTE_LABEL}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Horizontal(
                        Label(INSTANCE_LABEL, classes=FORM_LABEL_FIELD),
                        self.instance_input),
                    Horizontal(
                        Label(IP_ADDR_LABEL, classes=FORM_LABEL_FIELD),
                        self.ip_addr_input),
                    Horizontal(
                        Label(RPC_BIND_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.rpc_bind_port_input),
                    Horizontal(
                        Label(ZMQ_PUB_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.zmq_pub_port_input),
                    classes=FORM_4_FIELD),

                Vertical(
                    self.health_msgs,
                    classes=HEALTH_BOX_FIELD),

                Horizontal(
                    self.new_button,
                    self.update_button,
                    self.delete_button,
                    classes=BUTTON_ROW_FIELD)),

            classes=PANE_BOX_FIELD)     


    def set_data(self, monerod: MoneroDRemote):
        #(f"MonerodRemote:set_data(): rec: {rec}")
        self.instance_input.value = monerod.instance()
        self.ip_addr_input.value = monerod.ip_addr()
        self.rpc_bind_port_input.value = str(monerod.rpc_bind_port())
        self.zmq_pub_port_input.value = str(monerod.zmq_pub_port())
        self.health_msgs.update(gen_results_table(monerod.pop_msgs()))
        self.monerod = monerod
        # Set update button or new button visibility, using the .tcss definitions
        if monerod.instance():
            # This is an update operation
            self.remove_class(NEW_FIELD)
            self.add_class(UPDATE_FIELD)

        else:
            # This is a new operation
            self.remove_class(UPDATE_FIELD)
            self.add_class(NEW_FIELD)
        

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        self.monerod.instance(self.query_one("#instance_input", Input).value)
        self.monerod.ip_addr(self.query_one("#ip_addr_input", Input).value)
        self.monerod.rpc_bind_port(self.query_one("#rpc_bind_port_input", Input).value)
        self.monerod.zmq_pub_port(self.query_one("#zmq_pub_port_input", Input).value)


        if button_id == NEW_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                ELEMENT_FIELD: self.monerod,
            }                

        elif button_id == UPDATE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: JOB_QUEUE_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: UPDATE_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                ELEMENT_FIELD: self.monerod,
                INSTANCE_FIELD: self.monerod.instance(),
            }

        elif button_id == DELETE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: JOB_QUEUE_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: DELETE_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                INSTANCE_FIELD: self.monerod.instance(),
            }
        else:
            raise ValueError(f"No handler for {button_id}")
        self.app.post_message(Db4eMsg(self, form_data=form_data))
        #self.app.post_message(RefreshNavPane(self))