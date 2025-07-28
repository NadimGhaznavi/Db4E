"""
db4e/Panes/XMRig.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from rich import box
from rich.table import Table
from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Label, Input, Button, RadioSet, RadioButton, Static)

from db4e.Modules.Helper import gen_results_table
from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, BUTTON_ROW_FIELD, COMPONENT_FIELD, CONFIG_FIELD,
    DELETE_BUTTON_FIELD, DELETE_DEPLOYMENT_FIELD, DEPLOYMENT_MGR_FIELD,
    FORM_3_FIELD, FORM_INPUT_15_FIELD, FORM_INPUT_7_FIELD, FORM_INTRO_FIELD,
    FORM_LABEL_FIELD, GREEN_BUTTON_FIELD, HEALTH_BOX_FIELD, HEALTH_MSGS_FIELD,
    INSTANCE_FIELD, NEW_BUTTON_FIELD, NUM_THREADS_FIELD, OPS_MGR_FIELD,
    ORIG_INSTANCE_FIELD, P2POOL_INSTANCE, PANE_BOX_FIELD, PARENT_ID_FIELD,
    RADIO_BUTTON_TYPE_FIELD, RADIO_MAP_FIELD, RADIO_SET_FIELD, RED_BUTTON_FIELD,
    REMOTE_FIELD, STATIC_CONTENT_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD,
    UPDATE_BUTTON_FIELD, UPDATE_DEPLOYMENT_FIELD, XMRIG_FIELD
)
from db4e.Constants.Labels import (
    CONFIG_LABEL, DELETE_LABEL, UPDATE_LABEL, HEALTH_LABEL, INSTANCE_LABEL,
    NUM_THREADS_LABEL, P2POOL_LABEL, XMRIG_LABEL, NEW_LABEL
)

BUTTON_CONFIG = [
    {
        "id": "update",
        "label": "Update",
        "classes": GREEN_BUTTON_FIELD,
        "visible_in": ["active"],
        "enabled_in": ["active"],
    },
    {
        "id": "new",
        "label": "New",
        "classes": GREEN_BUTTON_FIELD,
        "visible_in": ["pending", "archived", "disabled"],
        "enabled_in": ["pending", "archived", "disabled"],
    },
    {
        "id": "delete",
        "label": "Delete",
        "classes": RED_BUTTON_FIELD,
        "visible_in": ["active", "disabled"],
        "enabled_in": ["disabled"],
    },
]

color = "#9cae41"
hi = "#d7e556"

class XMRig(Container):

    radio_button_list = reactive(list, always_update=True)
    radio_set = RadioSet(id="radio_set", classes=RADIO_SET_FIELD)

    p2pool_instance = ""
    instance_map = {}
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=FORM_INPUT_15_FIELD)
    num_threads_input = Input(
        id="num_threads_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_7_FIELD)
    config_static = Label("", id="config_static", classes=STATIC_CONTENT_FIELD)
    health_msgs = Static()

    def compose(self):
        # Remote P2Pool daemon deployment form
        INTRO = f"[{color}]View and edit the deployment settings for the " \
            f"[{hi}]{XMRIG_LABEL}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Horizontal(
                        Label(INSTANCE_LABEL, classes=FORM_LABEL_FIELD),
                        self.instance_input),
                    Horizontal(
                        Label(NUM_THREADS_LABEL, classes=FORM_LABEL_FIELD),
                        self.num_threads_input),
                    Horizontal(
                        Label(CONFIG_LABEL, classes=FORM_LABEL_FIELD),
                        self.config_static),
                    classes=FORM_3_FIELD),

                Vertical(
                    self.radio_set),

                Vertical(
                    self.health_msgs,
                    classes=HEALTH_BOX_FIELD),

                Vertical(
                    Horizontal(
                        Button(label=UPDATE_LABEL, id=UPDATE_BUTTON_FIELD, 
                               classes=GREEN_BUTTON_FIELD),
                        Button(label=NEW_LABEL, id=NEW_BUTTON_FIELD, 
                               classes=GREEN_BUTTON_FIELD),
                        Button(label=DELETE_LABEL, id=DELETE_BUTTON_FIELD, 
                               classes=RED_BUTTON_FIELD),
                        classes=BUTTON_ROW_FIELD))),
                
            classes=PANE_BOX_FIELD)

    def get_p2pool_id(self, instance=None):
        if instance and instance in self.instance_map:
            return self.instance_map[instance]
        return False

    def get_p2pool_instances(self):
        return self.instance_map

    def refresh_self(self, rec):
        pass


    def set_p2pool_instances(self, instance_map):
        print(f"XMRig:set_p2pool_instances:(): {instance_map}")
        self.instance_map = instance_map

    def set_data(self, rec):
        print(f"XMRig:set_data(): {rec}")
        self.instance_input.value = rec[INSTANCE_FIELD]
        self.orig_instance = rec[INSTANCE_FIELD]
        self.num_threads_input.value = str(rec[NUM_THREADS_FIELD])
        self.config_static.update(rec[CONFIG_FIELD])

        self.set_p2pool_instances(rec[RADIO_MAP_FIELD])
        self.p2pool_instance = rec[P2POOL_INSTANCE]  # Save it to use during watch

        # Trigger RadioButton recreation via reactive update
        self.radio_button_list = list(rec[RADIO_MAP_FIELD].keys())

        self.health_msgs.update(gen_results_table(rec[HEALTH_MSGS_FIELD]))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == UPDATE_BUTTON_FIELD:
            if self.orig_instance:
                to_method = UPDATE_DEPLOYMENT_FIELD
            else:
                to_method = ADD_DEPLOYMENT_FIELD
            radio_set = self.query_one("#radio_set", RadioSet)
            is_radiobutton = radio_set.pressed_button
            p2pool_instance = None
            if is_radiobutton:
                p2pool_instance = radio_set.pressed_button.label
            p2pool_id = self.get_p2pool_id(p2pool_instance)
            form_data = {
                COMPONENT_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: to_method,
                REMOTE_FIELD: False,
                ORIG_INSTANCE_FIELD: self.orig_instance,
                PARENT_ID_FIELD : p2pool_id,
                INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
                NUM_THREADS_FIELD: self.query_one("#num_threads_input", Input).value,
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
            radio_button = RadioButton(instance, classes=RADIO_BUTTON_TYPE_FIELD)
            self.radio_set.mount(radio_button)
            if instance == self.p2pool_instance:
                radio_button.value = instance