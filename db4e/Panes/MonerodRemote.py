"""
db4e/Panes/MonerodRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from rich import box
from rich.table import Table

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Label, MarkdownViewer, Button, Input, Static

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DELETE_DEPLOYMENT_FIELD,  DEPLOYMENT_MGR_FIELD, FORM_DATA_FIELD, 
    INSTANCE_FIELD, IP_ADDR_FIELD, MONEROD_FIELD, ORIG_INSTANCE_FIELD, 
    RPC_BIND_PORT_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD, 
    UPDATE_DEPLOYMENT_FIELD, ZMQ_PUB_PORT_FIELD
)
from db4e.Constants.Labels import (
    DELETE_LABEL, INSTANCE_LABEL, IP_ADDR_LABEL, MONEROD_REMOTE_LABEL, 
    RPC_BIND_PORT_LABEL, UPDATE_LABEL, ZMQ_PUB_PORT_LABEL
)

class MonerodRemote(Container):

    instance_input = Input(id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True)
    ip_addr_input = Input(id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True)
    rpc_bind_port_input = Input(id="rpc_bind_port_input", restrict=f"[0-9]*", compact=True)
    zmq_pub_port_input = Input(id="zmq_pub_port_input", restrict=f"[0-9]*", compact=True)
    health_msgs = Static()

    def build_health_status(self, results):
        table = Table(show_header=True, header_style="bold cyan", style="bold green", box=box.SIMPLE)
        table.add_column("Component", width=25)
        table.add_column("Message")

        for task in results:
            print(task)
            for category, msg_dict in task.items():
                message = msg_dict["msg"]
                if msg_dict["status"] == "good":
                    table.add_row(f"✅ [green]{category}[/]", f"[green]{message}[/]")
                elif msg_dict["status"] == "warn":
                    table.add_row(f"⚠️  [yellow]{category}[/]", f"[yellow]{message}[/]")
                elif msg_dict["status"] == "error":
                    table.add_row(f"💥 [red]{category}[/]", f"[red]{message}[/]")
        self.health_msgs.update(table)
        
    def compose(self):
        # Remote Monero daemon deployment form
        STATIC_CONTENT = f"This screen allows you to view and edit the deployment "
        STATIC_CONTENT += f"settings for the {MONEROD_REMOTE_LABEL} deployment."

        yield Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(INSTANCE_LABEL, id="instance_label"),
                    self.instance_input),
                Horizontal(
                    Label(IP_ADDR_LABEL, id="ip_addr_label"),
                    self.ip_addr_input),
                Horizontal(
                    Label(RPC_BIND_PORT_LABEL, id="rpc_bind_port_label"),
                    self.rpc_bind_port_input),
                Horizontal(
                    Label(ZMQ_PUB_PORT_LABEL, id="zmq_pub_port_label"),
                    self.zmq_pub_port_input),
                classes="form_box"),

            Horizontal(
                Button(label=UPDATE_LABEL, id="update_button"),
                Button(label=DELETE_LABEL, id="delete_button"),
                id="buttons"),

            Vertical(
                self.health_msgs,
                id="health_box",
            ))            

    def set_data(self, rec):

        self.orig_instance = rec[INSTANCE_FIELD]

        self.instance_input.value = rec[INSTANCE_FIELD]
        self.ip_addr_input.value = rec[IP_ADDR_FIELD]
        self.rpc_bind_port_input.value = str(rec[RPC_BIND_PORT_FIELD])
        self.zmq_pub_port_input.value = str(rec[ZMQ_PUB_PORT_FIELD])
        self.build_health_status(rec[HEALTH_MSG_FIELD])
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "update_button":
            form_data = {
                COMPONENT_FIELD: MONEROD_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
                FORM_DATA_FIELD: True,
                ORIG_INSTANCE_FIELD: self.orig_instance,
                INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
                IP_ADDR_FIELD: self.query_one("#ip_addr_input", Input).value,
                RPC_BIND_PORT_FIELD: self.query_one("#rpc_bind_port_input", Input).value,
                ZMQ_PUB_PORT_FIELD: self.query_one("#zmq_pub_port_input", Input).value,
            }
        else:
            form_data = {
                COMPONENT_FIELD: MONEROD_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: DELETE_DEPLOYMENT_FIELD,
                COMPONENT_FIELD: MONEROD_FIELD,
                INSTANCE_FIELD: self.orig_instance
            }
        self.app.post_message(SubmitFormData(self, form_data=form_data))