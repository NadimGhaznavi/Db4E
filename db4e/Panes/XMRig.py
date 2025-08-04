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

from db4e.Modules.Helper import gen_results_table, get_component_value
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, BUTTON_ROW_FIELD, CONFIG_FIELD,
    DELETE_BUTTON_FIELD, DELETE_DEPLOYMENT_FIELD, DEPLOYMENT_MGR_FIELD,
    FORM_3_FIELD, FORM_INPUT_15_FIELD, FORM_INPUT_7_FIELD, FORM_INTRO_FIELD,
    FORM_LABEL_FIELD, GREEN_BUTTON_FIELD, HEALTH_BOX_FIELD, HEALTH_MSGS_FIELD,
    INSTANCE_FIELD, NEW_BUTTON_FIELD, NUM_THREADS_FIELD, OPS_MGR_FIELD,
    ORIG_INSTANCE_FIELD, FORM_DATA_FIELD, PANE_BOX_FIELD, PARENT_ID_FIELD,
    RADIO_BUTTON_TYPE_FIELD, RADIO_MAP_FIELD, RADIO_SET_FIELD, RED_BUTTON_FIELD,
    REMOTE_FIELD, STATIC_CONTENT_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD,
    UPDATE_BUTTON_FIELD, UPDATE_DEPLOYMENT_FIELD, XMRIG_FIELD, ELEMENT_TYPE_FIELD,
    PARENT_INSTANCE_FIELD
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

class XMRig(Container):

    radio_button_list = reactive(list, always_update=True)
    radio_set = RadioSet(id="radio_set", classes=RADIO_SET_FIELD)

    instance_map = {}
    config_static = Label("", id="config_static", classes=STATIC_CONTENT_FIELD)
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=FORM_INPUT_15_FIELD)
    num_threads_input = Input(
        id="num_threads_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_15_FIELD)
    health_msgs = Static()

    def compose(self):
        # Remote P2Pool daemon deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{XMRIG_LABEL}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Horizontal(
                        Label(CONFIG_LABEL, classes=FORM_LABEL_FIELD),
                        self.config_static),
                    Horizontal(
                        Label(INSTANCE_LABEL, classes=FORM_LABEL_FIELD),
                        self.instance_input),
                    Horizontal(
                        Label(NUM_THREADS_LABEL, classes=FORM_LABEL_FIELD),
                        self.num_threads_input),
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
                        Button(label=DELETE_LABEL, id=DELETE_BUTTON_FIELD, 
                               classes=RED_BUTTON_FIELD),
                        classes=BUTTON_ROW_FIELD))),
                
            classes=PANE_BOX_FIELD)

    def get_p2pool_id(self, instance=None):
        if instance and instance in self.instance_map:
            return self.instance_map[instance]
        return False

    def set_data(self, rec):
        #print(f"XMRig:set_data(): {rec}")
        self.instance_input.value = get_component_value(rec, INSTANCE_FIELD)
        self.orig_instance = get_component_value(rec, INSTANCE_FIELD)
        self.num_threads_input.value = str(get_component_value(rec, NUM_THREADS_FIELD))
        self.config_static.update(get_component_value(rec, CONFIG_FIELD))

        self.instance_map = rec[RADIO_MAP_FIELD]
        self.p2pool_id = get_component_value(rec, PARENT_ID_FIELD)

        #print(f"XMRig:set_data(): radio_map: {rec[RADIO_MAP_FIELD]}, p2pool_id: {self.p2pool_id}")

        # Trigger RadioButton recreation via reactive update
        self.radio_button_list = list(self.instance_map.keys())

        self.health_msgs.update(gen_results_table(rec[HEALTH_MSGS_FIELD]))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == UPDATE_BUTTON_FIELD:
            radio_set = self.query_one("#radio_set", RadioSet)
            is_radiobutton = radio_set.pressed_button
            p2pool_instance = None
            if is_radiobutton:
                p2pool_instance = radio_set.pressed_button.label
                self.p2pool_id = self.instance_map[p2pool_instance]

            if self.orig_instance:
                form_data = {
                    ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
                    REMOTE_FIELD: False,
                    FORM_DATA_FIELD: True,
                    ORIG_INSTANCE_FIELD: self.orig_instance,
                    PARENT_ID_FIELD : self.p2pool_id,
                    INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
                    NUM_THREADS_FIELD: self.query_one("#num_threads_input", Input).value,
                }
            else:
                form_data = {
                    ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
                    FORM_DATA_FIELD: True,
                    REMOTE_FIELD: False,
                    PARENT_ID_FIELD : self.p2pool_id,
                    INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
                    NUM_THREADS_FIELD: self.query_one("#num_threads_input", Input).value,
                }

        elif button_id == DELETE_BUTTON_FIELD:
            form_data = {
                ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: DELETE_DEPLOYMENT_FIELD,
                INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
            }            
        self.app.post_message(Db4eMsg(self, form_data=form_data))
        self.app.post_message(RefreshNavPane(self))

    def watch_radio_button_list(self, old, new):
        #print("XMRig:watch_radio_button_list():")
        for child in list(self.radio_set.children):
            child.remove()
        for instance in self.instance_map.keys():
            if self.p2pool_id == self.instance_map[instance]:
                radio_button = RadioButton(instance, classes=RADIO_BUTTON_TYPE_FIELD)
                radio_button.value = True
            else:
                radio_button = RadioButton(instance, classes=RADIO_BUTTON_TYPE_FIELD)
            self.radio_set.mount(radio_button)
