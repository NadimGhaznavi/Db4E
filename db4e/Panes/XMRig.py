"""
db4e/Panes/XMRig.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from rich import box
from rich.table import Table
from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Label, Input, Button, MarkdownViewer, RadioSet, RadioButton, Static)

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    COMPONENT_FIELD, CONFIG_FIELD, DELETE_DEPLOYMENT_FIELD, DEPLOYMENT_MGR_FIELD, 
    HEALTH_MSG_FIELD, INSTANCE_FIELD, NUM_THREADS_FIELD, ORIG_INSTANCE_FIELD, 
    P2POOL_INSTANCE, P2POOL_ID_FIELD, RADIO_MAP, REMOTE_FIELD, TO_MODULE_FIELD, 
    TO_METHOD_FIELD, UPDATE_DEPLOYMENT_FIELD, XMRIG_FIELD)
from db4e.Constants.Labels import (
    CONFIG_LABEL, DELETE_LABEL, HEALTH_LABEL, INSTANCE_LABEL, P2POOL_LABEL, 
    NUM_THREADS_LABEL, UPDATE_LABEL, XMRIG_LABEL)

class XMRig(Container):

    radio_button_list = reactive(list, always_update=True)
    radio_set = RadioSet(id="radio_set")

    p2pool_instance = ""
    instance_map = {}
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True)
    num_threads_input = Input(
        id="num_threads_input", restrict=f"[0-9]*", compact=True)
    orig_instance_input = Input(id="orig_instance_input", classes="hidden")
    config_static = Static("", id="config_static")
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
        # Remote P2Pool daemon deployment form
        STATIC_CONTENT = "This screen provides a form for viewing and/or updating a "
        STATIC_CONTENT += f"{XMRIG_LABEL} deployment."

        yield Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(CONFIG_LABEL, id="config_label"),
                    self.config_static,
                ),
                Horizontal(
                    Label(INSTANCE_LABEL, id="instance_label"),
                    self.instance_input),
                Horizontal(
                    Label(NUM_THREADS_LABEL, id="num_threads_label"),
                    self.num_threads_input),
                id="xmrig_edit_form"),

            Vertical(
                Label(P2POOL_LABEL, id="p2pool_label"),
                self.radio_set,
                id="radio_set_box"),

            self.orig_instance_input,

            Horizontal(
                Button(label=UPDATE_LABEL, id="update_button"),
                Button(label=DELETE_LABEL, id="delete_button"),
                id="buttons"),
            
            Vertical(
                self.health_msgs,
                id="health_box",
            ),

        id="pane")

    def get_p2pool_id(self, instance=None):
        return self.instance_map[instance]

    def get_p2pool_instances(self):
        return self.instance_map

    def set_p2pool_instances(self, instance_map):
        self.instance_map = instance_map

    def set_data(self, rec):
        self.instance_input.value = rec[INSTANCE_FIELD]
        self.orig_instance_input.value = rec[INSTANCE_FIELD]
        self.num_threads_input.value = rec[NUM_THREADS_FIELD]
        self.p2pool_instance = rec[P2POOL_INSTANCE]
        self.config_static.update(rec[CONFIG_FIELD])
        self.set_p2pool_instances(rec[RADIO_MAP])
        instance_list = []
        for instance in rec[RADIO_MAP].keys():
            instance_list.append(instance)
        instance_list = self.radio_button_list + instance_list
        self.radio_button_list = [*instance_list]
        self.build_health_status(rec[HEALTH_MSG_FIELD])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "update_button":
            radio_set = self.query_one("#radio_set", RadioSet)
            is_radiobutton = radio_set.pressed_button
            p2pool_instance = None
            if is_radiobutton:
                p2pool_instance = radio_set.pressed_button.label
            p2pool_id = self.get_p2pool_id(p2pool_instance)
            form_data = {
                COMPONENT_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
                REMOTE_FIELD: False,
                INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
                ORIG_INSTANCE_FIELD: self.query_one("#orig_instance_input", Input).value,
                NUM_THREADS_FIELD: self.query_one("#num_threads_input", Input).value,
                P2POOL_ID_FIELD: p2pool_id
            }
        else:
            form_data = {
                COMPONENT_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: DELETE_DEPLOYMENT_FIELD,
                INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
            }            
        self.app.post_message(SubmitFormData(self, form_data=form_data))

    def watch_radio_button_list(self, old, new):
        for child in list(self.radio_set.children):
            child.remove()
        for instance in self.get_p2pool_instances().keys():
            radio_button = RadioButton(instance)
            self.radio_set.mount(radio_button)
            if instance == self.p2pool_instance:
                radio_button.value = True